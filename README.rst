**This is a Zabbix template + discovery & sender script useful to monitor Varnish Cache Plus instances**:

1. Copy ``zabbix-varnish-cache.py`` to ``/usr/local/bin/``.

2. Add ``zabbix`` user to the ``varnish`` group::

    $ sudo usermod -a --groups varnish zabbix

3. Grant sudo permissions to the ``zabbix`` user to execute the ``/usr/local/bin/zabbix-varnish-cache.py`` script. This is not mandatory but it's recommended in order to let the script execute ``varnishadm`` commands used to discover the current active VCL, discover healthiness of each backend, etc.

4. Add the ``varnish.discovery`` and ``varnish.stats`` user parameters to Zabbix::

    UserParameter=varnish.discovery[*],sudo /usr/local/bin/zabbix-varnish-cache.py -i '$1' discover $2
    UserParameter=varnish.stats[*],sudo /usr/local/bin/zabbix-varnish-cache.py -i '$1' stats

5. Import the Varnish Cache Plus template (``template-app-varnish.xml`` file).

6. Add an existing / new host to the ``Varnish Cache servers`` group and link it to the ``Template App Varnish Cache`` template. Beware you must set a value for the ``{$VARNISH_CACHE_LOCATIONS}`` macro (comma-delimited list of Varnish Cache Plus instance names). Usually you should leave its value blank when running a single Varnish Cache Plus instance per server. The following macros are available:

   * ``{$VARNISH_CACHE_AGENT_INSTANCES}``
   * ``{$VARNISH_CACHE_ALLOCATOR_FAILS_ALLOWED}``
   * ``{$VARNISH_CACHE_BACKEND_CONN_FAILURES_ALLOWED}``
   * ``{$VARNISH_CACHE_BROADCASTER_INSTANCES}``
   * ``{$VARNISH_CACHE_HIGH_N_OF_THREADS}``
   * ``{$VARNISH_CACHE_HISTORY_STORAGE_PERIOD}``
   * ``{$VARNISH_CACHE_INSTANCES}``
   * ``{$VARNISH_CACHE_LAST_VALUES_TO_CHECK}``
   * ``{$VARNISH_CACHE_LIMIT_SPARE_NODES}``
   * ``{$VARNISH_CACHE_LOCATIONS}``
   * ``{$VARNISH_CACHE_LOSTHDR_ALLOWED}``
   * ``{$VARNISH_CACHE_LOW_MSE_BOOK_SPACE}``
   * ``{$VARNISH_CACHE_LOW_SPARE_NODES}``
   * ``{$VARNISH_CACHE_MAIN_MIN_UPTIME_AFTER_RESTART}``
   * ``{$VARNISH_CACHE_MGT_MIN_UPTIME_AFTER_RESTART}``
   * ``{$VARNISH_CACHE_NCSA_INSTANCES}``
   * ``{$VARNISH_CACHE_NUKE_LIMIT}``
   * ``{$VARNISH_CACHE_RAW_LOG_INSTANCES}``
   * ``{$VARNISH_CACHE_TREND_STORAGE_PERIOD}``
   * ``{$VARNISH_CACHE_UPDATE_INTERVAL_DISCOVERY}``
   * ``{$VARNISH_CACHE_UPDATE_INTERVAL_ITEM}``
   * ``{$VARNISH_CACHE_VCL_FAILURES_ALLOWED}``
   * ``{$VARNISH_CACHE_WORKSPACE_OVERFLOWS_ALLOWED}``

   It's also possible to use **contexts** on macros, for example:

   * ``{$VARNISH_CACHE_HISTORY_STORAGE_PERIOD:items:sess_dropped}``
   * ``{$VARNISH_CACHE_TREND_STORAGE_PERIOD:items:backend_req}``

7. Adjust triggers and trigger prototypes according with your preferences.
