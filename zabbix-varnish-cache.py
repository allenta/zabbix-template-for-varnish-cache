#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
:url: https://github.com/allenta/zabbix-template-for-varnish-cache
:copyright: (c) 2015-2019 by Allenta Consulting S.L. <info@allenta.com>.
:license: BSD, see LICENSE.txt for more details.
'''

from __future__ import absolute_import, division, print_function, unicode_literals
import json
import re
import subprocess
import sys
from argparse import ArgumentParser, ArgumentTypeError

ITEMS = re.compile(
    r'^(?:'
    # Uptime.
    r'MAIN\.uptime|'
    r'MGT\.uptime|'
    # Client requests: rate.
    r'MAIN\.client_req|'
    r'MAIN\.s_req|'  # XXX: VCP 4.1
    # Client requests: activity.
    r'MAIN\.req_dropped|'
    r'MAIN\.client_req_400|'
    r'MAIN\.client_req_417|'
    # Client requests: bytes received.
    r'MAIN\.s_pipe_in|'
    r'MAIN\.s_pipe_hdrbytes|'
    r'MAIN\.s_req_hdrbytes|'
    r'MAIN\.s_req_bodybytes|'
    # Client requests: bytes sent.
    r'MAIN\.s_pipe_out|'
    r'MAIN\.s_resp_bodybytes|'
    r'MAIN\.s_resp_hdrbytes|'
    # Client requests: busy.
    r'MAIN\.busy_sleep|'
    r'MAIN\.busy_wakeup|'
    r'MAIN\.busy_killed|'
    # Client requests: passes seen.
    r'MAIN\.s_pass|'
    # Client requests: synthetic responses made.
    r'MAIN\.s_synth|'
    # Client sessions: rate.
    r'MAIN\.sess_conn|'
    # Client sessions: activity.
    r'MAIN\.s_sess|'
    r'MAIN\.sess_closed|'
    r'MAIN\.sess_closed_err|'
    r'MAIN\.sess_drop|'
    r'MAIN\.sess_dropped|'
    r'MAIN\.sess_fail|'
    r'MAIN\.sess_queued|'
    r'MAIN\.sess_readahead|'
    # Client sessions: failures.
    r'MAIN\.sess_fail_econnaborted|'
    r'MAIN\.sess_fail_eintr|'
    r'MAIN\.sess_fail_emfile|'
    r'MAIN\.sess_fail_ebadf|'
    r'MAIN\.sess_fail_enomem|'
    r'MAIN\.sess_fail_other|'
    # Client sessions: waiting for threads.
    r'MAIN\.thread_queue_len|'
    # Client sessions: pipes seen.
    r'MAIN\.s_pipe|'
    # Cache.
    r'MAIN\.cache_hit|'
    r'MAIN\.cache_hit_grace|'
    r'MAIN\.cache_hitpass|'
    r'MAIN\.cache_hitmiss|'
    r'MAIN\.cache_miss|'
    # HTTP header overflows.
    r'MAIN\.losthdr|'
    # Threads: number.
    r'MAIN\.threads|'
    # Threads: activity.
    r'MAIN\.threads_created|'
    r'MAIN\.threads_failed|'
    r'MAIN\.threads_limited|'
    r'MAIN\.threads_destroyed|'
    # ESI: activity.
    r'MAIN\.esi_warnings|'
    r'MAIN\.esi_errors|'
    r'MAIN\.esi_maxdepth|'
    # Gzip: activity.
    r'MAIN\.n_gzip|'
    r'MAIN\.n_gunzip|'
    r'MAIN\.n_test_gunzip|'
    # Objects: stored.
    r'MAIN\.n_object|'
    r'MAIN\.n_objecthead|'
    r'MAIN\.n_objectcore|'
    # Objects: removals.
    r'MAIN\.n_expired|'
    r'MAIN\.n_lru_nuked|'
    r'MAIN\.n_lru_moved|'
    r'MAIN\.n_obj_purged|'
    r'MAIN\.bans_obj_killed|'
    r'MAIN\.bans_lurker_obj_killed|'
    r'MAIN\.bans_lurker_obj_killed_cutoff|'
    # Objects: nuke limit overflows.
    r'MAIN\.n_lru_limited|'
    # Objects: purges.
    r'MAIN\.n_purges|'
    # Objects: bans.
    r'MAIN\.bans|'
    # Backends: connections rate.
    r'MAIN\.backend_conn|'
    # Backends: connections activity.
    r'MAIN\.backend_recycle|'
    r'MAIN\.backend_reuse|'
    r'MAIN\.backend_retry|'
    r'MAIN\.backend_busy|'
    r'MAIN\.backend_unhealthy|'
    r'MAIN\.backend_fail|'
    # Backends: request rate.
    r'MAIN\.backend_req|'
    # Backends: fetches activity.
    r'MAIN\.s_fetch|'
    r'MAIN\.fetch_head|'
    r'MAIN\.fetch_length|'
    r'MAIN\.fetch_chunked|'
    r'MAIN\.fetch_eof|'
    r'MAIN\.fetch_none|'
    r'MAIN\.fetch_1xx|'
    r'MAIN\.fetch_204|'
    r'MAIN\.fetch_304|'
    r'MAIN\.fetch_bad|'
    r'MAIN\.fetch_failed|'
    r'MAIN\.fetch_no_thread|'
    # Backends: number.
    r'MAIN\.n_backend|'
    # VCLs: number.
    r'MAIN\.n_vcl|'
    # VCLs: failures.
    r'MAIN\.sc_vcl_failure|'
    r'MAIN\.vcl_fail|'
    # VMODs: number.
    r'MAIN\.vmods|'
    # VMODs: goto.
    r'MAIN\.goto_dns_cache_hits|'
    r'MAIN\.goto_dns_lookup_fails|'
    r'MAIN\.goto_dns_lookups|'
    # VMODs: http.
    r'VMOD_HTTP\.handle_requests|'
    r'VMOD_HTTP\.handle_completed|'
    r'VMOD_HTTP\.handle_abandon|'
    # Workspace overflows.
    r'MAIN\.client_resp_500|'
    r'MAIN\.ws_backend_overflow|'
    r'MAIN\.ws_client_overflow|'
    r'MAIN\.ws_session_overflow|'
    r'MAIN\.ws_thread_overflow|'
    # VHA6.
    r'KVSTORE\.vha6_stats\..+\.(?:broadcast_candidates|broadcast_nocache|broadcast_skip|broadcast_lowttl|broadcast_toolarge|broadcasts|fetch_self|fetch_peer|fetch_origin|fetch_origin_deliver|fetch_peer_insert|error_version_mismatch|error_no_token|error_bad_token|error_stale_token|error_rate_limited|error_fetch_insert|error_origin_mismatch|error_origin_miss)|'
    # KVStore-based counters.
    r'KVSTORE\.counters\..+\..+|'
    # Storages[...]
    #   - Bytes outstanding vs. available: g_bytes, g_space.
    #   - Allocator failures: c_fail.
    #   - Nukes: n_lru_nuked, n_lru_moved.
    #   - Spare nodes available: g_sparenode (XXX: VCP 4.1)
    #   - Vary headers: n_vary.
    #   - YKeys: g_ykey_keys.
    #   - Cache: c_memcache_hit, c_memcache_miss.
    r'(?:MSE|SMA|SMF)\..+\.(?:c_fail|c_memcache_hit|c_memcache_miss|g_bytes|g_space|g_sparenode|g_ykey_keys|n_lru_nuked|n_lru_moved|n_vary)|'
    # MSE books[...]
    #   - Bytes outstanding vs. available: g_bytes, g_space.
    #   - Vary headers: n_vary.
    #   - Waterlevel: c_waterlevel_queue, c_waterlevel_runs, c_waterlevel_purge.
    #   - Banlist journal file bytes outstanding vs. available: g_banlist_bytes, g_banlist_space.
    #   - Timed out DB insertions: c_insert_timeout
    r'MSE_BOOK\..+\.(?:c_insert_timeout|c_waterlevel_purge|c_waterlevel_queue|c_waterlevel_runs|g_bytes|g_banlist_bytes|g_banlist_space|g_space|n_vary)|'
    # MSE stores[...]
    #   - Extents: g_alloc_bytes, g_free_bytes.
    #   - Objects: g_objects.
    #   - YKeys: g_ykey_keys.
    #   - AIO operations: c_aio_finished_read, c_aio_finished_write.
    #   - AIO bytes read/written: c_aio_finished_bytes_read, c_aio_finished_bytes_write.
    #   - Waterlevel: c_waterlevel_queue, c_waterlevel_purge.
    r'MSE_STORE\..+\.(?:c_aio_finished_read|c_aio_finished_write|c_aio_finished_bytes_read|c_aio_finished_bytes_write|c_waterlevel_purge|c_waterlevel_queue|g_alloc_bytes|g_free_bytes|g_objects|g_ykey_keys)|'
    # Backends[...]
    #   - Healthiness: happy.
    #   - Requests sent to backend: req.
    #   - Concurrent connections to backend: conn.
    #   - Fetches not attempted: unhealthy, busy, fail, helddown.
    #   - Failed connection attempts: fail_eacces, fail_eaddrnotavail, fail_econnrefused, fail_enetunreach, fail_etimedout, fail_other.
    #   - Bytes sent to backend: pipe_out, pipe_hdrbytes, bereq_hdrbytes, bereq_bodybytes.
    #   - Bytes received from backend: pipe_in, beresp_hdrbytes, beresp_bodybytes.
    r'VBE\..+\.(?:bereq_bodybytes|bereq_hdrbytes|beresp_bodybytes|beresp_hdrbytes|busy|conn|fail|fail_eacces|fail_eaddrnotavail|fail_econnrefused|fail_enetunreach|fail_etimedout|fail_other|happy|helddown|pipe_hdrbytes|pipe_in|pipe_out|req|unhealthy)'
    r')$')

LITE_FILTER = re.compile(
    r'VBE\..*')

REWRITES = [
    (re.compile(r'^KVSTORE\.vha6_stats\.[^\.]+'), r'VHA6'),
    (re.compile(r'^KVSTORE\.counters\.[^\.]+'), r'COUNTER'),
    (re.compile(r'^((?:MSE|SMA|SMF)\..+)$'), r'STG.\1'),
    (re.compile(r'^VBE\.(?:[^\.\(]+)((?:\.[^\.]*(?:\([^\)]*\))?)+\.[^\.]+)$'), r'VBE\1'),
    (re.compile(r'^(VBE\.goto)\.[0-9a-f]+\.\([^\)]*\)\.(.+)$'), r'\1.\2'),
]

SUBJECTS = {
    'items': None,
    'counters': re.compile(r'^COUNTER\.(.+)$'),
    'mse_books': re.compile(r'^MSE_BOOK\.(.+)\.[^\.]+$'),
    'mse_stores': re.compile(r'^MSE_STORE\.(.+)\.[^\.]+$'),
    'storages': re.compile(r'^STG\.(.+)\.[^\.]+$'),
    'backends': re.compile(r'^VBE\.(.+)\.[^\.]+$'),
}


###############################################################################
## 'stats' COMMAND
###############################################################################

def stats(options):
    # Initializations.
    result = {}

    # Build master item contents.
    for instance in options.varnish_instances.split(','):
        instance = instance.strip()
        items = _stats(instance, options.backends_re, lite=options.lite)
        for name, item in items.items():
            result['%(instance)s.%(name)s' % {
                'instance': _safe_zabbix_string(instance),
                'name': _safe_zabbix_string(name),
            }] = item['value']

    # Render output.
    sys.stdout.write(json.dumps(result, separators=(',', ':')))


################################################################################
## 'discover' COMMAND
###############################################################################

def discover(options):
    # Initializations.
    discovery = {
        'data': [],
    }

    # Build Zabbix discovery input.
    for instance in options.varnish_instances.split(','):
        instance = instance.strip()
        if options.subject == 'items':
            discovery['data'].append({
                '{#LOCATION}': instance,
                '{#LOCATION_ID}': _safe_zabbix_string(instance),
            })
        else:
            items = _stats(instance,options.backends_re)
            ids = set()
            for name in items.keys():
                match = SUBJECTS[options.subject].match(name)
                if match is not None and match.group(1) not in ids:
                    discovery['data'].append({
                        '{#LOCATION}': instance,
                        '{#LOCATION_ID}': _safe_zabbix_string(instance),
                        '{#SUBJECT}': match.group(1),
                        '{#SUBJECT_ID}': _safe_zabbix_string(match.group(1)),
                    })
                    ids.add(match.group(1))

    # Render output.
    sys.stdout.write(json.dumps(discovery, sort_keys=True, indent=2))


###############################################################################
## HELPERS
###############################################################################

class Rewriter(object):
    def __init__(self, rules):
        self._rules = rules

    def rewrite(self, name):
        result = name
        for pattern, repl in self._rules:
            if pattern.match(result):
                result = pattern.sub(repl, result)
        return result


def _stats(instance, backends_re, lite=False):
    # Fetch backends through varnishadm.
    backends = {}
    # rc, output = _execute('varnishadm %(name)s backend.list -j' % {
    rc, output = _execute('varnishadm %(name)s backend.list' % {
        'name': '-n "%s"' % instance,
    })
    if rc == 0:
        # for name, backend in json.loads(output)[3].items():
        #     if backend['type'] == 'backend':
        #         backends[name] = (backend['probe_message'] == 'healthy')
        for i, line in enumerate(output.split('\n')):
            if i > 0:
                items = line.split()
                if len(items) > 3:
                    backends[items[0]] = (items[2] == 'Healthy')
    else:
        backends = None
        sys.stderr.write(output)

    # Fetch stats through varnishstat & filter / normalize output.
    rc, output = _execute('varnishstat -1 -j %(name)s' % {
        'name': '-n "%s"' % instance,
    })
    if rc == 0:
        rewriter = Rewriter(REWRITES)
        result = {}
        for name, item in json.loads(output).items():
            if 'value' in item:
                if ITEMS.match(name) is not None:
                    if (not name.startswith('VBE.') or
                        backends is None or
                        any(name.startswith('VBE.' + backend + '.') for backend in backends.keys())) and \
                       (not lite or
                        LITE_FILTER.match(name) is None):
                        # Rewrite key.
                        key = rewriter.rewrite(name)

                        # If this is a backend item apply the backends filter.
                        if key.startswith('VBE.'):
                            match = SUBJECTS['backends'].match(key)
                            if match is not None and backends_re.search(match.group(1)) is None:
                                continue

                        # Process item and add it to the result.
                        value = {
                            'flag': item.get('flag'),
                            'description': item.get('description'),
                            'value': item['value'],
                        }
                        if key in result:
                            if value['flag'] in ('c', 'g'):
                                result[key]['value'] += value['value']
                            else:
                                result[key]['value'] = None
                        else:
                            result[key] = value

        # Add 'healthy' items to every backend.
        if backends is not None:
            for backend, healthy in backends.items():
                key = rewriter.rewrite('VBE.' + backend + '.healthy')
                match = SUBJECTS['backends'].match(key)
                if match is not None and backends_re.search(match.group(1)) is not None:
                    result[key] = {
                        'flag': 'g',
                        'description': '',
                        'value': int(healthy),
                    }
        return dict([
            (key, value)
            for key, value in result.items()
            if value['value'] is not None
        ])
    else:
        sys.stderr.write(output)
        sys.exit(1)


def _safe_zabbix_string(value):
    # Return a modified version of 'value' safe to be used as part of:
    #   - A quoted key parameter (see https://www.zabbix.com/documentation/4.0/manual/config/items/item/key).
    #   - A JSON string.
    return value.replace('"', '\\"')


def _execute(command, stdin=None):
    child = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    output = child.communicate(
        input=stdin.encode('utf-8') if stdin is not None else None)[0].decode('utf-8')
    return child.returncode, output


def re_argtype(string):
    try:
        return re.compile(string)
    except re.error as e:
        raise ArgumentTypeError(e)


###############################################################################
## MAIN
###############################################################################

def main():
    # Set up the base command line parser.
    parser = ArgumentParser()
    parser.add_argument(
        '-i', '--varnish-instances', dest='varnish_instances',
        type=str, required=True,
        help='comma-delimited list of Varnish Cache instances to get stats from')
    parser.add_argument(
        '-b', '--backends', dest='backends_re',
        type=re_argtype, default='.*',
        help='regular expression to match backends to be included (defaults to'
             ' all backends: ".*")')
    subparsers = parser.add_subparsers(dest='command')

    # Set up 'stats' command.
    subparser = subparsers.add_parser(
        'stats',
        help='collect Varnish Cache stats')
    subparser.add_argument(
        '--lite', dest='lite', action='store_true',
        help='enable lite mode')

    # Set up 'discover' command.
    subparser = subparsers.add_parser(
        'discover',
        help='generate Zabbix discovery schema')
    subparser.add_argument(
        'subject', type=str, choices=SUBJECTS.keys(),
        help='dynamic resources to be discovered')

    # Parse command line arguments.
    options = parser.parse_args()

    # Execute command.
    globals()[options.command](options)
    sys.exit(0)

if __name__ == '__main__':
    main()
