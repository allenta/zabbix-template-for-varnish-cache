varnish.5.1-repository:
  pkgrepo.managed:
    - name: deb https://packagecloud.io/varnishcache/varnish51/ubuntu/ trusty main
    - humanname: Varnish 5.1
    - key_url: https://packagecloud.io/varnishcache/varnish51/gpgkey
    - file: /etc/apt/sources.list.d/varnish.list
    - require_in:
      - pkg: varnish.packages

varnish.packages:
  pkg.installed:
    - refresh: True
    - pkgs:
      - varnish

varnish.varnish-service:
  service.running:
    - name: varnish
    - require:
      - pkg: varnish.packages

varnish.varnish-settings:
  file.append:
    - name: /etc/default/varnish
    - text: DAEMON_OPTS="${DAEMON_OPTS} -p sigsegv_handler=on"
    - watch_in:
      - service: varnish.varnish-service
    - require:
      - pkg: varnish.packages
