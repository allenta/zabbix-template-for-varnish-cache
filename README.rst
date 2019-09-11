**This is a Zabbix template + discovery & sender script useful to monitor Varnish Cache Plus instances**:

1. Copy ``zabbix-varnish-cache.py`` to ``/usr/local/bin/``.

2. Add ``zabbix`` user to the ``varnish`` group::

    $ sudo usermod -a --groups varnish zabbix

3. Grant sudo permissions to the ``zabbix`` user to execute the ``/usr/local/bin/zabbix-varnish-cache.py`` script. This is not mandatory but it's recommended in order to let the script execute ``varnishadm`` commands used to discover the current active VCL, discover healthiness of each backend, etc.

4. Add the ``varnish.discovery`` and ``varnish.stats`` user parameters to Zabbix::

    UserParameter=varnish.discovery[*],sudo /usr/local/bin/zabbix-varnish-cache.py -i '$1' discover $2
    UserParameter=varnish.stats[*],sudo /usr/local/bin/zabbix-varnish-cache.py -i '$1' stats

5. Import the Varnish Cache Plus template (``template-app-varnish.xml`` file).

6. Add an existing / new host to the ``Varnish Cache servers`` group and link it to the ``Template App Varnish Cache`` template. Beware you must set a value for the ``{$VARNISH_CACHE.LOCATIONS}`` macro (comma-delimited list of Varnish Cache Plus instance names). Usually you should leave its value blank when running a single Varnish Cache Plus instance per server. The following macros are available:

   * ``{$VARNISH_CACHE.LOCATIONS}``

   * ``{$VARNISH_CACHE.ALLOCATOR_FAILURES_RATE.MAX}``
   * ``{$VARNISH_CACHE.HTTP_HEADER_OVERFLOWS_RATE.MAX}``
   * ``{$VARNISH_CACHE.VCL_FAILURES_RATE.MAX}``
   * ``{$VARNISH_CACHE.WORKSPACE_OVERFLOWS_RATE.MAX}``

   * ``{$VARNISH_CACHE.BACKEND_CONNECTION_FAILURES_RATE.MAX}``
   * ``{$VARNISH_CACHE.LRU_NUKED_OBJECTS_RATE.MAX}``
   * ``{$VARNISH_CACHE.NUKE_LIMIT_REACHS_RATE.MAX}``

   * ``{$VARNISH_CACHE.AGENT_PROCESSES.MIN}``
   * ``{$VARNISH_CACHE.BROADCASTER_PROCESSES.MIN}``
   * ``{$VARNISH_CACHE.VARNISH_PROCESSES.MIN}``
   * ``{$VARNISH_CACHE.NCSA_PROCESSES.MIN}``
   * ``{$VARNISH_CACHE.RAW_LOG_PROCESSES.MIN}``
   * ``{$VARNISH_CACHE.VCS_AGENT_PROCESSES}``

   * ``{$VARNISH_CACHE.THREADS.MAX}``
   * ``{$VARNISH_CACHE.MSE_BOOK_SPACE.MIN}``
   * ``{$VARNISH_CACHE.MAIN_UPTIME.MIN}``
   * ``{$VARNISH_CACHE.MGT_UPTIME.MIN}

   * ``{$VARNISH_CACHE.SPARE_NODES.MIN.CRIT}``
   * ``{$VARNISH_CACHE.SPARE_NODES.MIN.WARN}``

   * ``{$VARNISH_CACHE.ITEM_HISTORY_STORAGE_PERIOD}``
   * ``{$VARNISH_CACHE.ITEM_TREND_STORAGE_PERIOD}``
   * ``{$VARNISH_CACHE.LLD_UPDATE_INTERVAL}``
   * ``{$VARNISH_CACHE.ITEM_UPDATE_INTERVAL}``
   * ``{$VARNISH_CACHE.LLD_KEEP_LOST_RESOURCES_PERIOD}``

   * ``{$VARNISH_CACHE.LAST_VALUES_TO_CHECK}``

   It's also possible to use **contexts** on macros, for example:

   * ``{$VARNISH_CACHE.ITEM_HISTORY_STORAGE_PERIOD:items:sess_dropped}``
   * ``{$VARNISH_CACHE.ITEM_TREND_STORAGE_PERIOD:items:backend_req}``

7. Adjust triggers and trigger prototypes according with your preferences.
