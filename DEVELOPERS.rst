General tips
============

- Templates:
    1. ``http://192.168.100.172/zabbix``
        - Default username/password is ``Admin``/``zabbix``.

    2. In 'Configuration > Templates' click on 'Import' and select ``template-app-varnish.xml``.

    3. In 'Configuration > Hosts' click on 'Create host':
        - Host name: ``dev``
        - Group: ``Varnish Cache servers``
        - Linked templates: ``Template App Varnish Cache``

- Zabbix 101:
    1. ``http://192.168.100.172/zabbix``
        - Default username/password is ``Admin``/``zabbix``.

    2. In 'Configuration > Hosts' click on 'Create host':
        - Host name: ``dev``
        - New group: ``Varnish Cache servers``

    3. In 'Configuration > Templates' click on 'Create template':
        - Name: ``Template App Varnish Cache``
        - Group: ``Varnish Cache servers``
        - Hosts / templates: ``Varnish Cache servers > dev``

    4. In 'Configuration > Templates > Template App Varnish Cache' click on 'Discovery rules' and then on 'Create discovery rule':
        - Name: ``Discovery Varnish Cache (bytes)``
        - Type: ``Zabbix agent``
        - Key: ``varnish.discovery[-i 'bytes$']``
        - New application: ``Varnish Cache``

    5. In 'Configuration > Templates > Template App Varnish Cache' click on 'Discovery rules', then on 'Item prototypes' in the 'Discovery Varnish Cache (bytes)' row, and then on 'Create item prototype':
        - Name: ``{#NAME}``
        - Type: ``Zabbix trapper``
        - Key: ``varnish["{#KEY}"]``
        - Units: ``bytes``
        - Description: ``{#DESCRIPTION}``
