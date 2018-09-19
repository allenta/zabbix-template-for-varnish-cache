varnish.6.1-repository:
  pkgrepo.managed:
    - name: deb https://packagecloud.io/varnishcache/varnish61/ubuntu/ xenial main
    - humanname: Varnish 6.1
    - key_url: https://packagecloud.io/varnishcache/varnish61/gpgkey
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
