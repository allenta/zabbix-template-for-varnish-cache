varnish.6.0-repository:
  pkgrepo.managed:
    - name: deb https://packagecloud.io/varnishcache/varnish60/ubuntu/ xenial main
    - humanname: Varnish 6.0
    - key_url: https://packagecloud.io/varnishcache/varnish60/gpgkey
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
