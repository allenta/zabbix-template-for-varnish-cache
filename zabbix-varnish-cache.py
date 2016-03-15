#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
:url: https://github.com/allenta/zabbix-template-for-varnish-cache
:copyright: (c) 2015 by Allenta Consulting S.L. <info@allenta.com>.
:license: BSD, see LICENSE.txt for more details.
'''

from __future__ import absolute_import
import json
import re
import subprocess
import sys
import time
from argparse import ArgumentParser

ITEMS = re.compile(
    r'^(?:'
    r'MAIN\.uptime|'
    r'MAIN\.sess_conn|'
    r'MAIN\.sess_drop|'
    r'MAIN\.sess_fail|'
    r'MAIN\.client_req_400|'
    r'MAIN\.client_req_417|'
    r'MAIN\.client_req|'
    r'MAIN\.cache_hit|'
    r'MAIN\.cache_hitpass|'
    r'MAIN\.cache_miss|'
    r'MAIN\.backend_conn|'
    r'MAIN\.backend_unhealthy|'
    r'MAIN\.backend_busy|'
    r'MAIN\.backend_fail|'
    r'MAIN\.backend_reuse|'
    r'MAIN\.backend_recycle|'
    r'MAIN\.backend_retry|'
    r'MAIN\.fetch_head|'
    r'MAIN\.fetch_length|'
    r'MAIN\.fetch_chunked|'
    r'MAIN\.fetch_eof|'
    r'MAIN\.fetch_bad|'
    r'MAIN\.fetch_none|'
    r'MAIN\.fetch_1xx|'
    r'MAIN\.fetch_204|'
    r'MAIN\.fetch_304|'
    r'MAIN\.fetch_failed|'
    r'MAIN\.fetch_no_thread|'
    r'MAIN\.threads|'
    r'MAIN\.threads_limited|'
    r'MAIN\.threads_created|'
    r'MAIN\.threads_destroyed|'
    r'MAIN\.threads_failed|'
    r'MAIN\.thread_queue_len|'
    r'MAIN\.busy_sleep|'
    r'MAIN\.busy_wakeup|'
    r'MAIN\.busy_killed|'
    r'MAIN\.sess_queued|'
    r'MAIN\.sess_dropped|'
    r'MAIN\.n_object|'
    r'MAIN\.n_objectcore|'
    r'MAIN\.n_objecthead|'
    r'MAIN\.n_backend|'
    r'MAIN\.n_expired|'
    r'MAIN\.n_lru_nuked|'
    r'MAIN\.bans_obj_killed|'
    r'MAIN\.bans_lurker_obj_killed|'
    r'MAIN\.losthdr|'
    r'MAIN\.s_sess|'
    r'MAIN\.s_req|'
    r'MAIN\.s_pipe|'
    r'MAIN\.s_pass|'
    r'MAIN\.s_fetch|'
    r'MAIN\.s_synth|'
    r'MAIN\.s_req_hdrbytes|'
    r'MAIN\.s_req_bodybytes|'
    r'MAIN\.s_resp_hdrbytes|'
    r'MAIN\.s_resp_bodybytes|'
    r'MAIN\.s_pipe_hdrbytes|'
    r'MAIN\.s_pipe_in|'
    r'MAIN\.s_pipe_out|'
    r'MAIN\.sess_closed|'
    r'MAIN\.sess_closed_err|'
    r'MAIN\.sess_readahead|'
    r'MAIN\.backend_req|'
    r'MAIN\.bans|'
    r'MAIN\.n_purges|'
    r'MAIN\.n_obj_purged|'
    r'MAIN\.esi_errors|'
    r'MAIN\.esi_warnings|'
    r'MAIN\.n_gzip|'
    r'MAIN\.n_gunzip|'
    r'MGT\.uptime|'
    r'SMA\..+\.(?:c_fail|g_bytes|g_space)|'
    r'VBE\..+\.(?:happy|bereq_hdrbytes|bereq_bodybytes|beresp_hdrbytes|beresp_bodybytes|pipe_hdrbytes|pipe_out|pipe_in|conn|req)'
    r')$')

SUBJECTS = {
    'backends': re.compile(r'^VBE\.(.+)\.[^\.]+$'),
    'storages': re.compile(r'^SMA\.(.+)\.[^\.]+$'),
}


###############################################################################
## 'send' COMMAND
###############################################################################

def send(options):
    # Initializations.
    now = int(time.time())
    items = stats(options.varnish_name)

    # Build Zabbix sender input.
    rows = ''
    for name, item in items.items():
        row = '- varnish.stat["%(key)s"] %(tst)d %(value)d\n' % {
            'key': str2key(name),
            'tst': now,
            'value': item['value'],
        }
        sys.stdout.write(row)
        rows += row

    # Submit metrics.
    rc, output = execute('zabbix_sender -T -r -i - %(config)s %(server)s %(port)s %(host)s' % {
        'config':
            '-c "%s"' % options.zabbix_config
            if options.zabbix_config is not None else '',
        'server':
            '-z "%s"' % options.zabbix_server
            if options.zabbix_server is not None else '',
        'port':
            '-p %d' % options.zabbix_port
            if options.zabbix_port is not None else '',
        'host':
            '-s "%s"' % options.zabbix_host
            if options.zabbix_host is not None else '',
    }, stdin=rows)

    # Check return code.
    if rc == 0:
        sys.stdout.write(output)
    else:
        sys.stderr.write(output)
        sys.exit(1)


###############################################################################
## 'discover' COMMAND
###############################################################################

def discover(options):
    # Initializations.
    items = stats(options.varnish_name)

    # Build Zabbix discovery input.
    ids = set()
    discovery = {
        'data': [],
    }
    for name in items.iterkeys():
        match = SUBJECTS[options.subject].match(name)
        if match is not None and match.group(1) not in ids:
            discovery['data'].append({
                '{#NAME}': match.group(1),
                '{#ID}': str2key(match.group(1)),
            })
            ids.add(match.group(1))

    # Render output.
    sys.stdout.write(json.dumps(discovery, sort_keys=True, indent=2))


###############################################################################
## HELPERS
###############################################################################

def stats(name=None):
    # Fetch stats through varnishstat.
    rc, output = execute('varnishstat -1 -j %(name)s' % {
        'name': '-n "%s"' % name if name is not None else '',
    })

    # Check return code & filter / normalize output.
    if rc == 0:
        result = {}
        for name, item in json.loads(output).items():
            if 'value' in item:
                if ITEMS.match(name) is not None:
                    result[name] = {
                        'type': item.get('type'),
                        'ident': item.get('ident'),
                        'flag': item.get('flag'),
                        'description': item.get('description'),
                        'value': item['value'],
                    }
        return result
    else:
        sys.stderr.write(output)
        sys.exit(1)


def str2key(name):
    result = name
    for char in ['(', ')', ',']:
        result = result.replace(char, '\\' + char)
    return result


def execute(command, stdin=None):
    child = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    output = child.communicate(input=stdin)[0]
    return child.returncode, output


###############################################################################
## MAIN
###############################################################################

def main():
    # Set up the base command line parser.
    parser = ArgumentParser()
    parser.add_argument(
        '-n', '--varnish-name', dest='varnish_name',
        type=str, required=False, default=None,
        help='the varnishd instance to get stats from')
    subparsers = parser.add_subparsers(dest='command')

    # Set up 'send' command.
    subparser = subparsers.add_parser(
        'send',
        help='submit varnishstat output through Zabbix sender')
    subparser.add_argument(
        '-c', '--zabbix-config', dest='zabbix_config',
        type=str, required=False, default=None,
        help='the Zabbix agent configuration file to fetch the configuration '
             'from')
    subparser.add_argument(
        '-z', '--zabbix-server', dest='zabbix_server',
        type=str, required=False, default=None,
        help='hostname or IP address of the Zabbix server / Zabbix proxy')
    subparser.add_argument(
        '-p', '--zabbix-port', dest='zabbix_port',
        type=int, required=False, default=None,
        help='port number of server trapper running on the Zabbix server / '
             'Zabbix proxy')
    subparser.add_argument(
        '-s', '--zabbix-host', dest='zabbix_host',
        type=str, required=False, default=None,
        help='host name as registered in the Zabbix frontend')

    # Set up 'discover' command.
    subparser = subparsers.add_parser(
        'discover',
        help='generate Zabbix discovery schema')
    subparser.add_argument(
        'subject', type=str, choices=SUBJECTS.keys(),
        help="dynamic resources to be discovered")

    # Parse command line arguments.
    options = parser.parse_args()

    # Check required arguments.
    if options.command == 'send':
        if options.zabbix_config is None and options.zabbix_server is None:
            parser.print_help()
            sys.exit(1)

    # Execute command.
    globals()[options.command](options)
    sys.exit(0)

if __name__ == '__main__':
    main()
