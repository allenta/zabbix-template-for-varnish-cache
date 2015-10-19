varnish.4.1-repository:
  pkgrepo.managed:
    - name: deb https://repo.varnish-cache.org/ubuntu/ trusty varnish-4.1
    - humanname: Varnish 4.1
    - key_url: https://repo.varnish-cache.org/GPG-key.txt
    - file: /etc/apt/sources.list.d/varnish.list
    - enabled: 1
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
