varnish.weekly-repository:
  pkgrepo.managed:
    - name: deb https://packagecloud.io/varnishcache/varnish-weekly/ubuntu/ xenial main
    - humanname: Varnish weekly
    - key_url: https://packagecloud.io/varnishcache/varnish-weekly/gpgkey
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
