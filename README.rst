**This is a Zabbix template + script useful to monitor Varnish Cache Plus instances**:

1. Copy ``zabbix-varnish-cache.py`` to ``/usr/local/bin/``.

2. Add the ``varnish.discovery`` and ``varnish.stats`` user parameters to Zabbix::

    UserParameter=varnish.discovery[*],sudo /usr/local/bin/zabbix-varnish-cache.py -i '$1' discover $2
    UserParameter=varnish.stats[*],sudo /usr/local/bin/zabbix-varnish-cache.py -i '$1' stats

   You'll have to grant ``zabbix`` user sudo permissions to execute ``/usr/local/bin/zabbix-varnish-cache.py`` in order to let the script perform ``varnishadm`` commands to discover the current active VCL, discover healthiness of each backend, etc.

   If you'd rather not use sudo, then add ``zabbix`` user to the ``varnish`` group in order for the script to be able to retrieve as much data as possible::

    $ sudo usermod -a --groups varnish zabbix

3. Import the template. You may download the appropriate version from `the releases page <https://github.com/allenta/zabbix-template-for-varnish-cache/releases/latest/>`_ or generate it using the Jinja2 skeleton::

    $ pip install jinja2-cli
    $ PYTHONPATH=. jinja2 \
        -D version={6.0,6.2,6.4,7.0,7.2} \
        [-D name='Varnish Cache'] \
        [-D description=''] \
        [-D release='trunk'] \
        --extension=extensions.zabbix.ZabbixExtension --strict -o template.xml template-app-varnish-cache.j2

4. Link hosts to the template. Beware you must set a value for the ``{$VARNISH_CACHE.LOCATIONS}`` macro (comma-delimited list of Varnish Cache Plus instance names). Usually you should leave its value blank when running a single Varnish Cache Plus instance per server. Additional macros and contexts are available for further customizations.
