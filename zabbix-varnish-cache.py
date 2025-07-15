#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
:url: https://github.com/allenta/zabbix-template-for-varnish-cache
:copyright: (c) Allenta Consulting S.L. <info@allenta.com>.
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
    r'MAIN\.esi_req',
    r'MAIN\.s_req',  # XXX: VCP 4.1
    # Client requests: activity.
    r'MAIN\.req_dropped',
    r'MAIN\.req_reset',
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
    r'MAIN\.sc_bankrupt',
    r'MAIN\.sc_rapid_reset',
    r'MAIN\.sc_sock_closed',
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
    r'MAIN\.esi_req_abort',
    # Gzip: activity.
    r'MAIN\.n_gzip',
    r'MAIN\.n_gunzip',
    r'MAIN\.n_test_gunzip',
    # Objects: stored.
    r'MAIN\.n_object',
    r'MAIN\.n_objecthead',
    r'MAIN\.n_objectcore',
    r'MAIN\.n_object_hitmiss',
    r'MAIN\.n_object_hitpass',
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
    r'MAIN\.backend_wait',
    r'MAIN\.backend_wait_fail',
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
    r'MAIN\.bgfetch_no_thread',
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
    # VMODs: accounting.
    r'ACCG_DIAG\.set_key_failure',
    r'ACCG_DIAG\.out_of_key_slots',
    r'ACCG_DIAG\.key_without_namespace',
    r'ACCG_DIAG\.namespace_already_set',
    r'ACCG_DIAG\.namespace_undefined',
    r'ACCG_DIAG\.create_namespace_failure',
    r'ACCG_DIAG\.req_dropped',
    r'ACCG_DIAG\.bereq_dropped',
    # VMODs: goto.
    r'MAIN\.goto_dns_cache_hits',
    r'MAIN\.goto_dns_lookup_fails',
    r'MAIN\.goto_dns_lookups',
    # VMODs: http.
    r'VMOD_HTTP\.handle_requests',
    r'VMOD_HTTP\.handle_completed',
    r'VMOD_HTTP\.handle_abandon',
    r'VMOD_HTTP\.handle_internal_error',
    r'VMOD_HTTP\.handle_limited',
    # Workspace overflows.
    r'MAIN\.client_resp_500',
    r'MAIN\.ws_backend_overflow',
    r'MAIN\.ws_client_overflow',
    r'MAIN\.ws_session_overflow',
    r'MAIN\.ws_thread_overflow',
    # SHM: activity.
    r'MAIN\.shm_records',
    r'MAIN\.shm_flushes',
    r'MAIN\.shm_cont',
    r'MAIN\.shm_cycles',
    # Transit buffer.
    r'MAIN\.transit_stored',
    r'MAIN\.transit_buffered',
    # VHA6.
    r'KVSTORE\.vha6_stats\..+\.(?:broadcast_candidates|broadcast_nocache|broadcast_skip|broadcast_lowttl|broadcast_toolarge|broadcasts|fetch_self|fetch_peer|fetch_peer_hit|fetch_origin|fetch_origin_deliver|fetch_peer_insert|error_version_mismatch|error_no_token|error_bad_token|error_stale_token|error_rate_limited|error_fetch|error_fetch_insert|error_fetch_seal|error_localhost|error_origin_mismatch|error_origin_miss|error_max_broadcasts|error_fetch_self|legacy_vha)',
    # KVStore-based counters.
    r'KVSTORE\.counters\..+\..+',
    # Accounting[...].
    #   - Client > Requests: client_req_count
    #   - Client > Responses: client_200_count, client_304_count, client_404_count, client_503_count, client_2xx_count, client_3xx_count, client_4xx_count, client_5xx_count
    #   - Client > Bytes received from clients: client_req_hdrbytes, client_req_bodybytes
    #   - Client > Bytes transmitted to clients: client_resp_hdrbytes, client_resp_bodybytes
    #   - Client > Hits > Requests: client_hit_count, client_grace_hit_count
    #   - Client > Hits > Bytes received from clients: client_hit_req_hdrbytes, client_hit_req_bodybytes
    #   - Client > Hits > Bytes transmitted to clients: client_hit_resp_hdrbytes, client_hit_resp_bodybytes
    #   - Client > Misses > Requests: client_miss_count
    #   - Client > Misses > Bytes received from clients: client_miss_req_hdrbytes, client_miss_req_bodybytes
    #   - Client > Misses > Bytes transmitted to clients: client_miss_resp_hdrbytes, client_miss_resp_bodybytes
    #   - Client > Passes > Requests: client_pass_count
    #   - Client > Passes > Bytes received from clients: client_pass_req_hdrbytes, client_pass_req_bodybytes
    #   - Client > Passes > Bytes transmitted to clients: client_pass_resp_hdrbytes, client_pass_resp_bodybytes
    #   - Client > Synths > Requests: client_synth_count
    #   - Client > Synths > Bytes received from clients: client_synth_req_hdrbytes, client_synth_req_bodybytes
    #   - Client > Synths > Bytes transmitted to clients: client_synth_resp_hdrbytes, client_synth_resp_bodybytes
    #   - Client > Pipes > Requests: client_pipe_count
    #   - Client > Pipes > Bytes received from clients: client_pipe_req_hdrbytes, client_pipe_req_bodybytes
    #   - Client > Pipes > Bytes transmitted to clients: client_pipe_resp_hdrbytes, client_pipe_resp_bodybytes
    #   - Backend > Requests: backend_req_count
    #   - Backend > Responses: backend_200_count, backend_304_count, backend_404_count, backend_503_count, backend_2xx_count, backend_3xx_count, backend_4xx_count, backend_5xx_count
    #   - Backend > Bytes transmitted to backends: backend_req_hdrbytes, backend_req_bodybytes
    #   - Backend > Bytes received from backends: backend_resp_hdrbytes, backend_resp_bodybytes
    r'ACCG\..+\..+\.(?:client_req_count|client_req_hdrbytes|client_req_bodybytes|client_resp_hdrbytes|client_resp_bodybytes|client_hit_count|client_grace_hit_count|client_hit_req_hdrbytes|client_hit_req_bodybytes|client_hit_resp_hdrbytes|client_hit_resp_bodybytes|client_miss_count|client_miss_req_hdrbytes|client_miss_req_bodybytes|client_miss_resp_hdrbytes|client_miss_resp_bodybytes|client_pass_count|client_pass_req_hdrbytes|client_pass_req_bodybytes|client_pass_resp_hdrbytes|client_pass_resp_bodybytes|client_synth_count|client_synth_req_hdrbytes|client_synth_req_bodybytes|client_synth_resp_hdrbytes|client_synth_resp_bodybytes|client_pipe_count|client_pipe_req_hdrbytes|client_pipe_req_bodybytes|client_pipe_resp_hdrbytes|client_pipe_resp_bodybytes|client_200_count|client_304_count|client_404_count|client_503_count|client_2xx_count|client_3xx_count|client_4xx_count|client_5xx_count|backend_req_count|backend_req_hdrbytes|backend_req_bodybytes|backend_resp_hdrbytes|backend_resp_bodybytes|backend_200_count|backend_304_count|backend_404_count|backend_503_count|backend_2xx_count|backend_3xx_count|backend_4xx_count|backend_5xx_count)',
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
    # MSE4
    #   - Bytes in use vs. available: MSE4_MEM.g_bytes, MSE4_MEM.g_space.
    #   - Bytes in use: MSE4_MEM.g_bytes_ephemeral, MSE4_MEM.g_bytes_persisted, MSE4_MEM.g_bytes_pass, MSE4_MEM.g_bytes_reqbody, MSE4_MEM.g_bytes_synthetic, MSE4_MEM.g_bytes_buffer.
    #   - Objects: MSE4_MEM.g_objects, MSE4_MEM.g_objects_ephemeral, MSE4_MEM.g_objects_persisted, MSE4_MEM.g_objects_pass, MSE4_MEM.g_objects_reqbody, MSE4_MEM.g_objects_synthetic.
    #   - Allocations: MSE4_MEM.g_allocations, MSE4_MEM.c_allocation, MSE4_MEM.c_allocation_ephemeral, MSE4_MEM.c_allocation_persisted, MSE4_MEM.c_allocation_pass, MSE4_MEM.c_allocation_reqbody, MSE4_MEM.c_allocation_synthetic, MSE4_MEM.c_allocation_buffer, MSE4_MEM.c_allocation_failure.
    #   - Releases: MSE4_MEM.c_free, MSE4_MEM.c_free_ephemeral, MSE4_MEM.c_free_persisted, MSE4_MEM.c_free_pass, MSE4_MEM.c_free_reqbody, MSE4_MEM.c_free_synthetic, MSE4_MEM.c_free_buffer.
    #   - Evictions: MSE4_MEM.c_eviction, MSE4_MEM.c_eviction_failure, MSE4_MEM.c_eviction_reorder.
    #   - Vary headers: MSE4.g_varyspec.
    #   - YKeys: MSE4.g_ykey_keys.
    #   - Ykeys purged: MSE4.c_ykey_purged.
    #   - Cache: MSE4_MEM.c_memcache_hit, MSE4_MEM.c_memcache_miss.
    r'MSE4_MEM\.(?:g_bytes|g_space)',
    r'MSE4_MEM\.(?:g_bytes_ephemeral|g_bytes_persisted|g_bytes_pass|g_bytes_reqbody|g_bytes_synthetic|g_bytes_buffer)',
    r'MSE4_MEM\.(?:g_objects|g_objects_ephemeral|g_objects_persisted|g_objects_pass|g_objects_reqbody|g_objects_synthetic)',
    r'MSE4_MEM\.(?:g_allocations|c_allocation|c_allocation_ephemeral|c_allocation_persisted|c_allocation_pass|c_allocation_reqbody|c_allocation_synthetic|c_allocation_buffer|c_allocation_failure)',
    r'MSE4_MEM\.(?:c_free|c_free_ephemeral|c_free_persisted|c_free_pass|c_free_reqbody|c_free_synthetic|c_free_buffer)',
    r'MSE4_MEM\.(?:c_eviction|c_eviction_failure|c_eviction_reorder)',
    r'MSE4\.(?:g_varyspec)',
    r'MSE4\.(?:g_ykey_keys)',
    r'MSE4\.(?:c_ykey_purged)',
    r'MSE4_MEM\.(?:c_memcache_hit|c_memcache_miss)',
    # MSE4 books[...]
    #   - Online: MSE4_BOOK.foo.online.
    #   - Slots in use vs. available: MSE4_BOOK.foo.g_slots_used, MSE4_BOOK.foo.g_slots_unused.
    #   - Objects: MSE4_BOOK.foo.g_objects, MSE4_BOOK.foo.g_unreachable_objects.
    #   - Vary headers: MSE4_BOOK.foo.g_varyspec.
    #   - YKeys: MSE4_BOOK.foo.g_ykey_keys.
    #   - Ykeys purged: MSE4_BOOK.foo.c_ykey_purged.
    #   - Queues: MSE4_BOOK.foo.c_freeslot_queued, MSE4_BOOK.foo.g_freeslot_queue, MSE4_BOOK.foo.c_submitslot_queued, MSE4_BOOK.foo.g_submitslot_queue.
    #   - Banlist bytes in use vs. available: MSE4_BANJRN.foo.g_bytes, MSE4_BANJRN.foo.g_space.
    #   - Banlist size: MSE4_BANJRN.foo.g_bans.
    #   - Banlist overflow: MSE4_BANJRN.foo.g_overflow_bans, MSE4_BANJRN.foo.g_overflow_bytes.
    r'MSE4_BOOK\..+\.(?:online)',
    r'MSE4_BOOK\..+\.(?:g_slots_used|g_slots_unused)',
    r'MSE4_BOOK\..+\.(?:g_objects|g_unreachable_objects)',
    r'MSE4_BOOK\..+\.(?:g_varyspec)',
    r'MSE4_BOOK\..+\.(?:g_ykey_keys)',
    r'MSE4_BOOK\..+\.(?:c_ykey_purged)',
    r'MSE4_BOOK\..+\.(?:c_freeslot_queued|g_freeslot_queue|c_submitslot_queued|g_submitslot_queue)',
    r'MSE4_BANJRN\..+\.(?:g_bytes|g_space)',
    r'MSE4_BANJRN\..+\.(?:g_bans)',
    r'MSE4_BANJRN\..+\.(?:g_overflow_bans|g_overflow_bytes)',
    # MSE4 stores[...]
    #   - Online: MSE4_STORE.foo.bar.online.
    #   - Bytes in use vs. available: MSE4_STORE.foo.bar.g_bytes_used, MSE4_STORE.foo.bar.g_bytes_unused.
    #   - Reserve bytes: MSE4_STORE.foo.bar.g_reserve_bytes.
    #   - Objects: MSE4_STORE.foo.bar.g_objects.
    #   - Queues: MSE4_STORE.foo.bar.g_allocation_queue, MSE4_STORE.foo.bar.c_allocation_queued, MSE4_STORE.foo.bar.g_io_queued, MSE4_STORE.foo.bar.g_io_queued_read, MSE4_STORE.foo.bar.g_io_queued_write.
    #   - IO finished operations: MSE4_STORE.foo.bar.c_io_finished_read, MSE4_STORE.foo.bar.c_io_finished_write.
    #   - IO finished bytes: MSE4_STORE.foo.bar.c_io_finished_bytes_read, MSE4_STORE.foo.bar.c_io_finished_bytes_write.
    #   - IO blocked operations: MSE4_STORE.foo.bar.g_io_blocked_read, MSE4_STORE.foo.bar.g_io_blocked_write.
    #   - IO limited: MSE4_STORE.foo.bar.c_io_limited.
    r'MSE4_STORE\..+\.(?:online)',
    r'MSE4_STORE\..+\.(?:g_bytes_used|g_bytes_unused)',
    r'MSE4_STORE\..+\.(?:g_reserve_bytes)',
    r'MSE4_STORE\..+\.(?:g_objects)',
    r'MSE4_STORE\..+\.(?:g_allocation_queue|c_allocation_queued|g_io_queued|g_io_queued_read|g_io_queued_write)',
    r'MSE4_STORE\..+\.(?:c_io_finished_read|c_io_finished_write)',
    r'MSE4_STORE\..+\.(?:c_io_finished_bytes_read|c_io_finished_bytes_write)',
    r'MSE4_STORE\..+\.(?:g_io_blocked_read|g_io_blocked_write)',
    r'MSE4_STORE\..+\.(?:c_io_limited)',
    # MSE4 categories[...]
    #   - Bytes in use: MSE4_CAT.foo.bar.baz.g_bytes, MSE4_CAT.foo.bar.baz.g_bytes_ephemeral, MSE4_CAT.foo.bar.baz.g_bytes_persisted, MSE4_CAT.foo.bar.baz.g_bytes_pass.
    #   - Objects: MSE4_CAT.foo.bar.baz.g_objects, MSE4_CAT.foo.bar.baz.g_objects_ephemeral, MSE4_CAT.foo.bar.baz.g_objects_persisted, MSE4_CAT.foo.bar.baz.g_objects_pass.
    #   - Allocations: MSE4_CAT.foo.bar.baz.g_allocations, MSE4_CAT.foo.bar.baz.c_allocation, MSE4_CAT.foo.bar.baz.c_allocation_ephemeral, MSE4_CAT.foo.bar.baz.c_allocation_persisted, MSE4_CAT.foo.bar.baz.c_allocation_pass.
    #   - Releases: MSE4_CAT.foo.bar.baz.c_free, MSE4_CAT.foo.bar.baz.c_free_ephemeral, MSE4_CAT.foo.bar.baz.c_free_persisted, MSE4_CAT.foo.bar.baz.c_free_pass.
    #   - Evictions: MSE4_CAT.foo.bar.baz.c_eviction, MSE4_CAT.foo.bar.baz.c_eviction_failure, MSE4_CAT.foo.bar.baz.c_eviction_reorder.
    #   - Cache: MSE4_CAT.foo.bar.baz.c_memcache_hit, MSE4_CAT.foo.bar.baz.c_memcache_miss.
    r'MSE4_CAT\..+\.(?:g_bytes|g_bytes_ephemeral|g_bytes_persisted|g_bytes_pass)',
    r'MSE4_CAT\..+\.(?:g_objects|g_objects_ephemeral|g_objects_persisted|g_objects_pass)',
    r'MSE4_CAT\..+\.(?:g_allocations|c_allocation|c_allocation_ephemeral|c_allocation_persisted|c_allocation_pass)',
    r'MSE4_CAT\..+\.(?:c_free|c_free_ephemeral|c_free_persisted|c_free_pass)',
    r'MSE4_CAT\..+\.(?:c_eviction|c_eviction_failure|c_eviction_reorder)',
    r'MSE4_CAT\..+\.(?:c_memcache_hit|c_memcache_miss)',
    # Backends[...]
    #   - Healthiness: happy, healthy.
    #   - Requests sent to backend: req.
    #   - Concurrent connections to backend: conn.
    #   - Fetches not attempted: unhealthy, busy, fail, helddown.
    #   - Failed connection attempts: fail_eacces, fail_eaddrnotavail, fail_econnrefused, fail_enetunreach, fail_etimedout, fail_other.
    #   - Bytes sent to backend: pipe_out, pipe_hdrbytes, bereq_hdrbytes, bereq_bodybytes.
    #   - Bytes received from backend: pipe_in, beresp_hdrbytes, beresp_bodybytes.
    r'VBE\..+\.(?:bereq_bodybytes|bereq_hdrbytes|beresp_bodybytes|beresp_hdrbytes|busy|conn|fail|fail_eacces|fail_eaddrnotavail|fail_econnrefused|fail_enetunreach|fail_etimedout|fail_other|happy|helddown|pipe_hdrbytes|pipe_in|pipe_out|req|unhealthy|healthy)',
)

REWRITES = [
    # KVSTORE.vha6_stats.boot.foo -> VHA6.foo.
    (re.compile(r'^KVSTORE\.vha6_stats\.[^\.]+'), r'VHA6'),
    # KVSTORE.counters.boot.foo -> COUNTER.foo.
    (re.compile(r'^KVSTORE\.counters\.[^\.]+'), r'COUNTER'),
    # MSE.main.foo -> STG.MSE.main.foo. Beware MSE4 doesn't follow the same
    # pattern (i.e. <type>.<name>.<metric>) because on MSE4-enabled VCPs a
    # single MSE4 store can be used.
    (re.compile(r'^((?:MSE|SMA|SMF)\..+)$'), r'STG.\1'),
    # MSE4_CAT.(foo.bar).baz -> MSE4_CAT.foo.bar.baz
    (re.compile(r'^MSE4_CAT\.\(([^\)]+)\)\.'), r'MSE4_CAT.\1.'),
    # VBE.boot.foo.bar.baz -> VBE.foo.bar.baz
    (re.compile(r'^VBE\.[^\.]+'), r'VBE'),
    # VBE.goto.0000003f.(1.2.3.4).(http://foo.com:80).(ttl:10.000000) -> VBE.goto.(1.2.3.4).(http://foo.com:80).(ttl:10.000000)
    (re.compile(r'^VBE\.goto\.[0-9a-f]+'), r'VBE.goto'),
]

EXCLUSIONS = r'^ACCG\.(?!std\.)'

SUBJECTS = {
    'items': None,
    'counters': re.compile(r'^COUNTER\.(.+)$'),
    'accountings': re.compile(r'^ACCG\.([^\.]+\.[^\.]+)\.[^\.]+$'),
    'mse_books': re.compile(r'^MSE_BOOK\.(.+)\.[^\.]+$'),
    'mse_stores': re.compile(r'^MSE_STORE\.(.+)\.[^\.]+$'),
    'mse4_books': re.compile(r'^MSE4_BOOK\.(.+)\.[^\.]+$'),
    'mse4_stores': re.compile(r'^MSE4_STORE\.(.+)\.[^\.]+$'),
    'mse4_categories': re.compile(r'^MSE4_CAT\.(.+)\.[^\.]+$'),
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
        stats = _stats(instance, options.exclusions)
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
            stats = _stats(instance, options.exclusions)
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

    def __init__(self, items_definitions, subjects_patterns, exclusions, log_handler=None):
        # Build items regular expression that will be used to match item names
        # and discover item types.
        self._items_pattern = re.compile(
            r'^(?:' + '|'.join(items_definitions) + r')$')

        # Set subject patterns that will be used to assign subject type and
        # subject values to items.
        self._subjects_patterns = subjects_patterns

        # Other initializations.
        self._exclusions = exclusions
        self._log_handler = log_handler or sys.stderr.write
        self._items = {}
        self._subjects = {}

    @property
    def items(self):
        # Return all items that haven't had their value discarded because an
        # invalid aggregation.
        return (item for item in self._items.values() if item.value is not None)

    def add(self, item):
        # Filter excluded items.
        if self._exclusions.match(item.name) is not None:
            return

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


def _stats(instance, exclusions):
    # Initializations.
    stats = Stats(ITEMS, SUBJECTS, exclusions)
    vbe_happy_pattern = re.compile(r'^VBE\..+\.happy$')

    # Fetch backends through varnishadm.
    backends = _backend_stats(stats, instance)

    # Fetch stats through varnishstat & filter / normalize output.
    rc, output = _execute('varnishstat -1 -j -n "{}"'.format(instance))
    if rc == 0:
        for name, data in json.loads(output).items():
            # Filter invalid items.
            if 'value' not in data:
                continue

            # Get item type.
            if data['flag'] == 'c':
                type = TYPE_COUNTER
            elif data['flag'] == 'g':
                type = TYPE_GAUGE
            else:
                type = TYPE_OTHER

            # 'VBE.*.happy' items are bitmaps storing results (i.e. success or
            # failure) of the last 64 backend probes. From the 'varnishstat'
            # point of view, those items are represented as 64 bit integers.
            # Submitting such big integer values to Zabbix is problematic:
            #   - Although Python (when parsing 'varnishstat' output & when
            #     dumping script output) and Zabbix (when extracting values from
            #     a JSON master item) are able to serialize / deserialize 64 bit
            #     ints in JSON values just fine, integer precission in a valid
            #     JSON value should be limited to 53 bits. Reason is that
            #     numeric values in JavaScript are internally coded as float64,
            #     which effectively limits precision of ints to 53 bits. A
            #     JavaScript post-processing of JSON values in Zabbix would hit
            #     the 53 bits limit because of the Duktape engine.
            #   - Although JavaScript post-processing is just a particular use
            #     case, in monitoring ecosystems it's general practice to assume
            #     ints are limited to 53 bits. For example, same limitation
            #     applies in the Prometheus exposition format where all metrics
            #     are float64. Approximations are possible, but that's far from
            #     ideal, and definitely is a no-go for bitmaps. From the
            #     Prometheus docs, to put the 53 bits limitation in perspective:
            #     'a counter, even if incremented one million times per second,
            #     will only run into precision issues after over 285 years'.
            #
            # Although the described limitation applies to all 'varnishstat'
            # values (all of them are int64) during a JavaScript post-processing
            # step in the Zabbix side, it only represents a realistic issue for
            # 'VBE.*.happy' items, and that's why here values of those items are
            # truncated to keep just the less significative 50 bits.
            value = data['value']
            if vbe_happy_pattern.match(name) is not None:
                value = value & (2**50 - 1)

            # Build item.
            item = stats.build_item(name, value, type)
            if item is None:
                continue

            # Filter out items from unknown backends (i.e. backends from other
            # warm or cold VCLs). This is only possible if the list of backends
            # was successfully fetched through varnishadm.
            if item.subject_type == 'backends' and \
               backends is not None and \
               item.subject_value not in backends:
                continue

            # Add item to the result.
            stats.add(item)

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


def _backend_stats(stats, instance):
    backends = None

    # XXX: since VCP 6.0.6r8 the 'is_healthy' item is included in varnishstat's
    # output. However fetching the list of backends through varnishadm is still
    # recommended in order to filter out backends associated to warm or cold
    # VCLs.

    # XXX: since VCP 6.0.8r4 a '-j' option is included that could easen parsing.
    # To be used when that version is widely adopted.

    rc, output = _execute('varnishadm -n "{}" backend.list'.format(instance))
    if rc == 0:
        backends = set()
        for line in output.split('\n')[1:]:
            items = line.split()
            if len(items) > 3:
                item = stats.build_item(
                    'VBE.' + items[0] + '.healthy',
                    1 if items[2] == 'Healthy' else 0,
                    TYPE_GAUGE)
                if item is not None:
                    assert item.subject_type == 'backends'
                    stats.add(item)
                    backends.add(item.subject_value)
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
                        value=int(fields[9]),
                        type=TYPE_COUNTER))
                    stats.add(Item(
                        name='PAGE_FAULTS.major',
                        value=int(fields[11]),
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
        '-e', '--exclusions', dest='exclusions',
        type=re_argtype, default=EXCLUSIONS,
        help='regular expression to match stats to be excluded (defaults to'
             ' "{}")'.format(EXCLUSIONS))
    subparsers = parser.add_subparsers(dest='command')

    # Set up 'stats' command.
    subparser = subparsers.add_parser(
        'stats',
        help='collect Varnish Cache stats')

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
    if options.command:
        globals()[options.command](options)
    else:
        parser.print_help()
        sys.exit(1)
    sys.exit(0)

if __name__ == '__main__':
    main()
