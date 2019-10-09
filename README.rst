**This is a Zabbix template + script useful to monitor Varnish Cache Plus instances**:

1. Copy ``zabbix-varnish-cache.py`` to ``/usr/local/bin/``.

2. Add ``zabbix`` user to the ``varnish`` group::

    $ sudo usermod -a --groups varnish zabbix

3. Grant sudo permissions to the ``zabbix`` user to execute the ``/usr/local/bin/zabbix-varnish-cache.py`` script. This is not mandatory but it's recommended in order to let the script execute ``varnishadm`` commands used to discover the current active VCL, discover healthiness of each backend, etc.

4. Add the ``varnish.discovery`` and ``varnish.stats`` user parameters to Zabbix. Beware additional arguments (e.g. ``--lite``, ``--exclude-backends``, etc.) might be required depending on the XML template generated during the next step::

    UserParameter=varnish.discovery[*],sudo /usr/local/bin/zabbix-varnish-cache.py -i '$1' discover $2
    UserParameter=varnish.stats[*],sudo /usr/local/bin/zabbix-varnish-cache.py -i '$1' stats

5. Generate the Varnish Cache Plus template using the Jinja2 skeleton and import it::

    $ pip install jinja2-cli
    $ jinja2 \
        -D version={4.0,4.2} \
        [-D name='Varnish Cache'] \
        [-D lite=0] \
        --strict -o template.xml template-app-varnish-cache.j2

6. Link hosts to the template. Beware you must set a value for the ``{$VARNISH_CACHE.LOCATIONS}`` macro (comma-delimited list of Varnish Cache Plus instance names). Usually you should leave its value blank when running a single Varnish Cache Plus instance per server. Additional macros and contexts are available for further customizations.
