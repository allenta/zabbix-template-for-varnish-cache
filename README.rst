**This is a Zabbix template + discovery & sender script useful to monitor Varnish Cache (5.2.x) instances**. Beware this project contains multiples branches (master, 4.1, etc.). Please, select the branch to be used depending on your Varnish Cache version (Varnish trunk → master, Varnish 4.1.x → 4.1, etc.):

1. Copy ``zabbix-varnish-cache.py`` to ``/usr/local/bin/``.

2. Add ``zabbix`` user to the ``varnish`` group::

    $ sudo usermod -a --groups varnish zabbix

3. Grant sudo permissions to the ``zabbix`` user to execute the ``/usr/local/bin/zabbix-varnish-cache.py`` script. This is not mandatory but it's recommended in order to let the script execute ``varnishadm`` commands used to discover the current active VCL, discover healthiness of each backend, etc.

4. Add the ``varnish.discovery`` user parameter to Zabbix::

    UserParameter=varnish.discovery[*],sudo /usr/local/bin/zabbix-varnish-cache.py -i '$1' discover $2

5. Add a new job to the ``zabbix`` user crontab (beware of the ``-i`` and ``-s`` options). This will submit Varnish Cache metrics through Zabbix Sender::

    * * * * * /usr/local/bin/zabbix-varnish-cache.py -i '' send -c /etc/zabbix/zabbix_agentd.conf -s dev > /dev/null 2>&1

6. Import the Varnish Cache template (``template-app-varnish.xml`` file).

7. Add an existing / new host to the ``Varnish Cache servers`` group and link it to the ``Template App Varnish Cache`` template. Beware you must set a value for the ``{$VARNISH_CACHE_LOCATIONS}`` macro (comma-delimited list of Varnish Cache instance names). Usually you should leave its value blank when running a single Varnish Cache instance per server. The following macros are available on both templates:

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
   * ``{$VARNISH_CACHE_LOW_SPARE_NODES}``
   * ``{$VARNISH_CACHE_MAIN_MIN_UPTIME_AFTER_RESTART}``
   * ``{$VARNISH_CACHE_MGT_MIN_UPTIME_AFTER_RESTART}``
   * ``{$VARNISH_CACHE_MIN_HEALTHY_BACKENDS}``
   * ``{$VARNISH_CACHE_NCSA_INSTANCES}``
   * ``{$VARNISH_CACHE_RAW_LOG_INSTANCES}``
   * ``{$VARNISH_CACHE_TREND_STORAGE_PERIOD}``
   * ``{$VARNISH_CACHE_UPDATE_INTERVAL_DISCOVERY}``
   * ``{$VARNISH_CACHE_UPDATE_INTERVAL_ITEM}``
   * ``{$VARNISH_CACHE_VCL_FAILURES_ALLOWED}``

   It's also possible to use **contexts** on macros, for example:

   * ``{$VARNISH_CACHE_HISTORY_STORAGE_PERIOD:req_dropped}``
   * ``{$VARNISH_CACHE_TREND_STORAGE_PERIOD:backend_req}``

8. Adjust triggers and trigger prototypes according with your preferences.
