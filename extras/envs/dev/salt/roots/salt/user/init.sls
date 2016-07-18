user.color-prompt:
  file.replace:
    - name: /home/vagrant/.bashrc
    - pattern: '#force_color_prompt=yes'
    - repl: 'force_color_prompt=yes'

user.zabbix-sender-cron:
  cron.present:
    - user: zabbix
    - name: /vagrant/zabbix-varnish-cache.py -i '' send -c /etc/zabbix/zabbix_agentd.conf -s dev > /dev/null 2>&1
    - require:
      - sls: zabbix
