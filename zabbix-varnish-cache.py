#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
:url: https://github.com/allenta/zabbix-template-for-varnish-cache
:copyright: (c) 2015-2021 by Allenta Consulting S.L. <info@allenta.com>.
:license: BSD, see LICENSE.txt for more details.
'''

from __future__ import absolute_import, division, print_function, unicode_literals
import json
import re
import socket
import subprocess
import sys
from argparse import ArgumentParser, ArgumentTypeError
from resource import getpagesize

TYPE_COUNTER = 1
TYPE_GAUGE = 2
TYPE_OTHER = 3
TYPES = (TYPE_COUNTER, TYPE_GAUGE, TYPE_OTHER)

ITEMS = (
    # Uptime.
    r'MAIN\.uptime',
    r'MGT\.uptime',
    # Worker process memory usage.
    r'MAIN\.g_mem_file',
    r'MAIN\.g_mem_private',
    r'MAIN\.g_mem_rss',
    r'MAIN\.g_mem_swap',
    # Client requests: rate.
    r'MAIN\.client_req',
    r'MAIN\.s_req',  # XXX: VCP 4.1
    # Client requests: activity.
    r'MAIN\.req_dropped',
    r'MAIN\.client_req_400',
    r'MAIN\.client_req_417',
    # Client requests: bytes received.
    r'MAIN\.s_pipe_in',
    r'MAIN\.s_pipe_hdrbytes',
    r'MAIN\.s_req_hdrbytes',
    r'MAIN\.s_req_bodybytes',
    # Client requests: bytes sent.
    r'MAIN\.s_pipe_out',
    r'MAIN\.s_resp_bodybytes',
    r'MAIN\.s_resp_hdrbytes',
    # Client requests: busy.
    r'MAIN\.busy_sleep',
    r'MAIN\.busy_wakeup',
    r'MAIN\.busy_killed',
    # Client requests: passes seen.
    r'MAIN\.s_pass',
    # Client requests: synthetic responses made.
    r'MAIN\.s_synth',
    # Client sessions: rate.
    r'MAIN\.sess_conn',
    # Client sessions: activity.
    r'MAIN\.s_sess',
    r'MAIN\.sess_closed',
    r'MAIN\.sess_closed_err',
    r'MAIN\.sess_drop',
    r'MAIN\.sess_dropped',
    r'MAIN\.sess_fail',
    r'MAIN\.sess_herd',
    r'MAIN\.sess_queued',
    r'MAIN\.sess_readahead',
    # Client sessions: failures.
    r'MAIN\.sess_fail_econnaborted',
    r'MAIN\.sess_fail_eintr',
    r'MAIN\.sess_fail_emfile',
    r'MAIN\.sess_fail_ebadf',
    r'MAIN\.sess_fail_enomem',
    r'MAIN\.sess_fail_other',
    # Client sessions: waiting for threads.
    r'MAIN\.thread_queue_len',
    # Client sessions: pipes seen.
    r'MAIN\.s_pipe',
    # Cache.
    r'MAIN\.cache_hit',
    r'MAIN\.cache_hit_grace',
    r'MAIN\.cache_hitpass',
    r'MAIN\.cache_hitmiss',
    r'MAIN\.cache_miss',
    # HTTP header overflows.
    r'MAIN\.losthdr',
    # Threads: number.
    r'MAIN\.threads',
    # Threads: activity.
    r'MAIN\.threads_created',
    r'MAIN\.threads_failed',
    r'MAIN\.threads_limited',
    r'MAIN\.threads_destroyed',
    # ESI: activity.
    r'MAIN\.esi_warnings',
    r'MAIN\.esi_errors',
    r'MAIN\.esi_maxdepth',
    # Gzip: activity.
    r'MAIN\.n_gzip',
    r'MAIN\.n_gunzip',
    r'MAIN\.n_test_gunzip',
    # Objects: stored.
    r'MAIN\.n_object',
    r'MAIN\.n_objecthead',
    r'MAIN\.n_objectcore',
    # Objects: removals.
    r'MAIN\.n_expired',
    r'MAIN\.n_lru_nuked',
    r'MAIN\.n_lru_moved',
    r'MAIN\.n_obj_purged',
    r'MAIN\.bans_obj_killed',
    r'MAIN\.bans_lurker_obj_killed',
    r'MAIN\.bans_lurker_obj_killed_cutoff',
    # Objects: nuke limit overflows.
    r'MAIN\.n_lru_limited',
    # Objects: purges.
    r'MAIN\.n_purges',
    r'MAIN\.c_ykey_purges',
    # Objects: bans.
    r'MAIN\.bans',
    # Backends: connections rate.
    r'MAIN\.backend_conn',
    # Backends: connections activity.
    r'MAIN\.backend_recycle',
    r'MAIN\.backend_reuse',
    r'MAIN\.backend_retry',
    r'MAIN\.backend_busy',
    r'MAIN\.backend_unhealthy',
    r'MAIN\.backend_fail',
    # Backends: request rate.
    r'MAIN\.backend_req',
    # Backends: fetches activity.
    r'MAIN\.s_fetch',
    r'MAIN\.fetch_head',
    r'MAIN\.fetch_length',
    r'MAIN\.fetch_chunked',
    r'MAIN\.fetch_eof',
    r'MAIN\.fetch_none',
    r'MAIN\.fetch_1xx',
    r'MAIN\.fetch_204',
    r'MAIN\.fetch_304',
    r'MAIN\.fetch_bad',
    r'MAIN\.fetch_failed',
    r'MAIN\.fetch_fast304',
    r'MAIN\.fetch_no_thread',
    r'MAIN\.fetch_stale_deliver',
    r'MAIN\.fetch_stale_rearm',
    # Backends: number.
    r'MAIN\.n_backend',
    # VCLs: number.
    r'MAIN\.n_vcl',
    # VCLs: failures.
    r'MAIN\.sc_vcl_failure',
    r'MAIN\.vcl_fail',
    # VMODs: number.
    r'MAIN\.vmods',
    # VMODs: goto.
    r'MAIN\.goto_dns_cache_hits',
    r'MAIN\.goto_dns_lookup_fails',
    r'MAIN\.goto_dns_lookups',
    # VMODs: http.
    r'VMOD_HTTP\.handle_requests',
    r'VMOD_HTTP\.handle_completed',
    r'VMOD_HTTP\.handle_abandon',
    # Workspace overflows.
    r'MAIN\.client_resp_500',
    r'MAIN\.ws_backend_overflow',
    r'MAIN\.ws_client_overflow',
    r'MAIN\.ws_session_overflow',
    r'MAIN\.ws_thread_overflow',
    # VHA6.
    r'KVSTORE\.vha6_stats\..+\.(?:broadcast_candidates|broadcast_nocache|broadcast_skip|broadcast_lowttl|broadcast_toolarge|broadcasts|fetch_self|fetch_peer|fetch_origin|fetch_origin_deliver|fetch_peer_insert|error_version_mismatch|error_no_token|error_bad_token|error_stale_token|error_rate_limited|error_fetch_insert|error_origin_mismatch|error_origin_miss)',
    # KVStore-based counters.
    r'KVSTORE\.counters\..+\..+',
    # Storages[...]
    #   - Bytes outstanding vs. available: g_bytes, g_space.
    #   - Allocator failures: c_fail.
    #   - Nukes: n_lru_nuked, n_lru_moved.
    #   - Spare nodes available: g_sparenode (XXX: VCP 4.1)
    #   - Vary headers: n_vary.
    #   - YKeys: g_ykey_keys.
    #   - Ykeys purged: c_ykey_purged.
    #   - Cache: c_memcache_hit, c_memcache_miss.
    r'(?:MSE|SMA|SMF)\..+\.(?:c_fail|c_memcache_hit|c_memcache_miss|c_ykey_purged|g_bytes|g_space|g_sparenode|g_ykey_keys|n_lru_nuked|n_lru_moved|n_vary)',
    # MSE books[...]
    #   - Bytes outstanding vs. available: g_bytes, g_space.
    #   - Vary headers: n_vary.
    #   - Waterlevel: c_waterlevel_queue, c_waterlevel_runs, c_waterlevel_purge.
    #   - Banlist journal file bytes outstanding vs. available: g_banlist_bytes, g_banlist_space.
    #   - Timed out DB insertions: c_insert_timeout
    r'MSE_BOOK\..+\.(?:c_insert_timeout|c_waterlevel_purge|c_waterlevel_queue|c_waterlevel_runs|g_bytes|g_banlist_bytes|g_banlist_space|g_space|n_vary)',
    # MSE stores[...]
    #   - Extents: g_alloc_bytes, g_free_bytes.
    #   - Objects: g_objects.
    #   - YKeys: g_ykey_keys.
    #   - AIO operations: c_aio_finished_read, c_aio_finished_write.
    #   - AIO bytes read/written: c_aio_finished_bytes_read, c_aio_finished_bytes_write.
    #   - Waterlevel: c_waterlevel_queue, c_waterlevel_purge.
    r'MSE_STORE\..+\.(?:c_aio_finished_read|c_aio_finished_write|c_aio_finished_bytes_read|c_aio_finished_bytes_write|c_waterlevel_purge|c_waterlevel_queue|g_alloc_bytes|g_free_bytes|g_objects|g_ykey_keys)',
    # Backends[...]
    #   - Healthiness: happy.
    #   - Requests sent to backend: req.
    #   - Concurrent connections to backend: conn.
    #   - Fetches not attempted: unhealthy, busy, fail, helddown.
    #   - Failed connection attempts: fail_eacces, fail_eaddrnotavail, fail_econnrefused, fail_enetunreach, fail_etimedout, fail_other.
    #   - Bytes sent to backend: pipe_out, pipe_hdrbytes, bereq_hdrbytes, bereq_bodybytes.
    #   - Bytes received from backend: pipe_in, beresp_hdrbytes, beresp_bodybytes.
    r'VBE\..+\.(?:bereq_bodybytes|bereq_hdrbytes|beresp_bodybytes|beresp_hdrbytes|busy|conn|fail|fail_eacces|fail_eaddrnotavail|fail_econnrefused|fail_enetunreach|fail_etimedout|fail_other|happy|helddown|pipe_hdrbytes|pipe_in|pipe_out|req|unhealthy)',
)

LITE_FILTER = re.compile(
    r'^VBE\..*')

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
        stats = _stats(instance, options.backends_re, lite=options.lite)
        for item in stats.items:
            result['%(instance)s.%(name)s' % {
                'instance': _safe_zabbix_string(instance),
                'name': _safe_zabbix_string(item.name),
            }] = item.value

    # Render output.
    sys.stdout.write(json.dumps(result, separators=(',', ':')))


###############################################################################
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
            stats = _stats(instance, options.backends_re)
            for subject in stats.subjects(options.subject):
                discovery['data'].append({
                    '{#LOCATION}': instance,
                    '{#LOCATION_ID}': _safe_zabbix_string(instance),
                    '{#SUBJECT}': subject,
                    '{#SUBJECT_ID}': _safe_zabbix_string(subject),
                })

    # Render output.
    sys.stdout.write(json.dumps(discovery, sort_keys=True, indent=2))


###############################################################################
## HELPERS
###############################################################################

class Item(object):
    '''
    A class to hold all relevant information about an item in the stats: name,
    value, type and subject (type & value).
    '''

    def __init__(
            self, name, value, type, subject_type=None, subject_value=None):
        # Set name and value.
        self._name = name
        self._value = value
        self._type = type
        self._subject_type = subject_type or 'items'
        self._subject_value = subject_value

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @property
    def type(self):
        return self._type

    @property
    def subject_type(self):
        return self._subject_type

    @property
    def subject_value(self):
        return self._subject_value

    def aggregate(self, value):
        # Aggregate another value. Only counter and gauges can be aggregated.
        # In any other case, mark this item's value as discarded.
        if self.type in (TYPE_COUNTER, TYPE_GAUGE):
            self._value += value
        else:
            self._value = None


class Stats(object):
    '''
    A class to hold results for a call to _stats: keeps all processed items and
    all subjects seen per subject type and provides helper methods to build and
    process those items.
    '''

    def __init__(self, items_definitions, subjects_patterns, log_handler=None):
        # Build items regular expression that will be used to match item names
        # and discover item types.
        self._items_pattern = re.compile(
            r'^(?:' + '|'.join(items_definitions) + r')$')

        # Set subject patterns that will be used to assign subject type and
        # subject values to items.
        self._subjects_patterns = subjects_patterns

        # Other initializations.
        self._log_handler = log_handler or sys.stderr.write
        self._items = {}
        self._subjects = {}

    @property
    def items(self):
        # Return all items that haven't had their value discarded because an
        # invalid aggregation.
        return (item for item in self._items.values() if item.value is not None)

    def add(self, item):
        # Add a new item to the internal state or simply aggregate it's value
        # if an item with the same name has already been added.
        if item.name in self._items:
            self._items[item.name].aggregate(item.value)
        else:
            # Add new item to the internal state.
            self._items[item.name] = item

            # Also, register this item's subject in the corresponding set.
            if item.subject_type != None and item.subject_value != None:
                if item.subject_type not in self._subjects:
                    self._subjects[item.subject_type] = set()
                self._subjects[item.subject_type].add(item.subject_value)

    def get(self, name, default=None):
        # Return current value for a particular item or the given default value
        # if that item is not available or has had it's value discarded.
        if name in self._items and self._items[name].value is not None:
            return self._items[name].value
        else:
            return default

    def subjects(self, subject_type):
        # Return the set of registered subjects for a given subject type.
        return self._subjects.get(subject_type, set())

    def log(self, message):
        self._log_handler(message)

    def build_item(
            self, name, value, type, subject_type=None,
            subject_value=None):
        # Filter invalid items.
        if self._items_pattern.match(name) is None:
            return None

        # Rewrite name.
        name = _rewrite(name)

        # Initialize subject_type and subject_value if none were provided.
        if subject_type is None and subject_value is None:
            for subject, subject_re in self._subjects_patterns.items():
                if subject_re is not None:
                    match = subject_re.match(name)
                    if match is not None:
                        subject_type = subject
                        subject_value = match.group(1)
                        break

        # Return item instance.
        return Item(
            name=name,
            value=value,
            type=type,
            subject_type=subject_type,
            subject_value=subject_value
        )


def _stats(instance, backends_re=None, lite=False):
    # Initializations.
    stats = Stats(ITEMS, SUBJECTS)

    # Fetch backends through varnishadm.
    backends = _backends(stats, instance)

    # Fetch stats through varnishstat & filter / normalize output.
    rc, output = _execute('varnishstat -1 -j -n "{}"'.format(instance))
    if rc == 0:
        for name, data in json.loads(output).items():
            # Filter invalid items.
            if 'value' not in data:
                continue

            # Filter non-lite items when in lite mode.
            if lite and LITE_FILTER.match(name) is not None:
                continue

            # Get item type.
            if data['flag'] == 'c':
                type = TYPE_COUNTER
            elif data['flag'] == 'g':
                type = TYPE_GAUGE
            else:
                type = TYPE_OTHER

            # Build item.
            item = stats.build_item(name, data['value'], type)
            if item is None:
                continue

            # Filter items from unknown backends.
            if item.subject_type == 'backends' and \
               backends is not None and \
               item.subject_value not in backends:
                continue

            # Filter items from ignored backends.
            if item.subject_type == 'backends' and \
               backends_re is not None and \
               backends_re.search(item.subject_value) is None:
                continue

            # Add item to the result.
            stats.add(item)

        # Add 'healthy' item to every backend. Do it iterating the backends
        # list and not the backends subjects list stored in stats because
        # no backend will be available there when lite option is set.
        # XXX: Since VCP 6.0.6r8 a 'is_healthy' item is already returned by
        # varnishstat, but healthiness is still being retrieved from varnishadm
        # in order to support lower VCP versions.
        if backends is not None:
            for backend in backends:
                if backends_re is None or \
                   backends_re.search(backend) is not None:
                    stats.add(Item(
                        name='VBE.{}.healthy'.format(backend),
                        value=int(backends[backend]),
                        type=TYPE_GAUGE,
                        subject_type='backends',
                        subject_value=backend))

        # Get worker process PID if possible (it is only available in VCP 6.x)
        # and use it to include memory and page fault stats.
        pid = _pid(instance)
        if pid is not None:
            _memory_stats(stats, pid)
            _page_fault_stats(stats, pid)

    # Error recovering information from varnishstat.
    else:
        stats.log(output)

    # Done!
    return stats


def _backends(stats, instance):
    backends = None

    # XXX: This varnishadm interaction has been rendered unnecessary since VCP
    # 6.0.6r8, as a 'is_healthy' item was included in varnishstat's output and,
    # as a fact, only backends associated to warm VCLs are being considered. As
    # for now, it is kept, though, in order to support lower VCP versions.

    # rc, output = _execute('varnishadm %(name)s backend.list -j' % {
    rc, output = _execute('varnishadm -n "{}" backend.list'.format(instance))
    if rc == 0:
        # for name, backend in json.loads(output)[3].items():
        #     if backend['type'] == 'backend':
        #         backends[name] = (backend['probe_message'] == 'healthy')
        backends = {}
        for line in output.split('\n')[1:]:
            items = line.split()
            if len(items) > 3:
                # Create a synthetic stat item name so that the final backend
                # name can be extracted.
                key = _rewrite('VBE.' + items[0] + '.foo')
                match = SUBJECTS['backends'].match(key)
                if match is not None:
                    backends[match.group(1)] = (items[2] == 'Healthy')
    else:
        stats.log(output)

    return backends


def _pid(instance):
    # Since VCP 6.0.6r7 it is possible to conveniently extract the worker PID
    # through varnishadm. For lower versions of VCP 6.x this information may
    # be extracted from an index file. For even lower versions (4.1) no PID
    # is returned.
    pid = None
    rc, output = _execute('varnishadm -n "{}" pid -j'.format(instance))
    if rc == 0:
        pid = int(json.loads(output)[3]['worker'])
    else:
        try:
            with open('/var/lib/varnish/%(name)s/_.vsm_child/_.index' % {
                'name': instance or socket.gethostname()
            }) as f:
                pid = int(f.readline().split(' ')[1])
        except IOError:
            pass
    return pid


def _memory_stats(stats, pid):
    # Linux is assumed. See:
    #   - man proc
    #   - https://www.zabbix.com/documentation/5.0/manual/config/items/itemtypes/zabbix_agent
    #   - https://www.zabbix.com/documentation/5.0/manual/appendix/items/proc_mem_notes
    #   - https://unix.stackexchange.com/questions/199482/does-proc-pid-status-always-use-kb
    try:
        with open('/proc/{}/statm'.format(pid), 'r') as fd:
            fields = fd.read().split()
            page_size = getpagesize()

            # Column #1 (pages) in /proc/<PID>/statm:
            #   - Total number of pages of memory.
            #   - 'VIRT' column in top.
            #   - Same as 'VmSize' (KiB) in /proc/<PID>/status.
            #   - Same as proc.mem[,,,,vsize].
            stats.add(Item(
                name='MEMORY.size',
                value=int(fields[0]) * page_size,
                type=TYPE_GAUGE))

            # Column #2 (pages) in /proc/<PID>/statm:
            #   - Number of resident set (non-swapped) pages.
            #   - 'RES' column in top.
            #   - Same as 'VmRSS' (KiB) in /proc/<PID>/status.
            #   - Same as proc.mem[,,,,rss].
            stats.add(Item(
                name='MEMORY.resident',
                value=int(fields[1]) * page_size,
                type=TYPE_GAUGE))

            # Column #3 (pages) in /proc/<PID>/statm:
            #   - Number of pages of shared (mmap'd) memory.
            #   - 'SHR' column in top.
            #   - Same as RssFile (KiB) + RssShmem (KiB) in some systems.
            #   - Not available vía Zabbix proc.mem[].
            stats.add(Item(
                name='MEMORY.shared',
                value=int(fields[2]) * page_size,
                type=TYPE_GAUGE))

            # Column #4 (pages) in /proc/<PID>/statm:
            #   - Text resident set size.
            #   - 'CODE' column in top.
            #   - Same as 'VmExe' (KiB) in /proc/<PID>/status.
            #   - Same as proc.mem[,,,,exe].
            stats.add(Item(
                name='MEMORY.text',
                value=int(fields[3]) * page_size,
                type=TYPE_GAUGE))

            # Column #6 (pages) in /proc/<PID>/statm:
            #   - Data + stack resident set size.
            #   - 'DATA' column in top.
            #   - Same as 'VmData' (KiB) + 'VmStk' (KiB) in /proc/<PID>/status.
            #   - Same as proc.mem[,,,,data] + proc.mem[,,,,stk].
            #   - Same as proc.mem[,,,,size] - proc.mem[,,,,exe].
            stats.add(Item(
                name='MEMORY.data',
                value=int(fields[5]) * page_size,
                type=TYPE_GAUGE))
    except:
        stats.log('Failed to fetch /proc/{}/statm stats'.format(pid))

    try:
        with open('/proc/{}/status'.format(pid), 'r') as fd:
            items = re.compile(r'^(VmSwap):\s*(\d+)\s*kB$')
            for line in fd:
                match = items.match(line)
                if match is not None:
                    name = match.group(1)
                    value = int(match.group(2)) * 1024
                    if name == 'VmSwap':
                        # 'VmSwap' (KiB) in /proc/<PID>/status:
                        #   - 'SWAP' column in top.
                        #   - Same as proc.mem[,,,,swap].
                        stats.add(Item(
                            name='MEMORY.swap',
                            value=value,
                            type=TYPE_GAUGE))
                        break
    except:
        stats.log('Failed to fetch /proc/{}/status stats'.format(pid))


def _page_fault_stats(stats, pid):
    # Linux is assumed. See:
    #   - man proc
    try:
        with open('/proc/{}/stat'.format(pid), 'r') as fd:
            for line in fd:
                fields = line.split(' ')
                if len(fields) > 11:
                    stats.add(Item(
                        name='PAGE_FAULTS.minor',
                        value=fields[9],
                        type=TYPE_COUNTER))
                    stats.add(Item(
                        name='PAGE_FAULTS.major',
                        value=fields[11],
                        type=TYPE_COUNTER))
                    break
    except:
        stats.log('Failed to fetch /proc/{}/stat stats'.format(pid))


def _rewrite(name):
    result = name
    for pattern, repl in REWRITES:
        if pattern.match(result):
            result = pattern.sub(repl, result)
    return result


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
