# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure('2') do |config|
  config.vm.box = 'allenta/ubuntu.xenial64'
  config.vm.box_version = '=20190320.0.1'
  config.vm.box_check_update = true
  config.ssh.forward_agent = true

  config.vm.provider :virtualbox do |vb|
    vb.memory = 2048
    vb.cpus = 1
    vb.linked_clone = Gem::Version.new(Vagrant::VERSION) >= Gem::Version.new('1.8.0')
    vb.customize [
      'modifyvm', :id,
      '--natdnshostresolver1', 'off',
      '--natdnsproxy1', 'on',
      '--accelerate3d', 'off',
      '--audio', 'none',
      '--paravirtprovider', 'Default',
      '--uartmode1', 'disconnected',
    ]
  end

  config.vm.hostname = 'dev'

  config.vm.network :public_network

  config.vm.synced_folder 'extras/envs/dev/ansible', '/srv/ansible', :nfs => false
  config.vm.synced_folder '.', '/vagrant', :nfs => false

  ansible_config = {
    :type => 'ansible_local',
    :playbook => '/srv/ansible/playbook.yml',
    :verbose => 'v',
    :extra_vars => {
      'settings' => {
        'mysql.root' => {
          'password' => 's3cr3t',
        },
        'mysql.zabbix' => {
          'name' => 'zabbix',
          'user' => 'zabbix',
          'password' => 'zabbix',
        },
      },
    },
    :install_mode => 'pip',
    :version => '2.6.4',
  }

  config.vm.define :v60, primary: true do |machine|
    machine.vm.provider :virtualbox do |vb|
      vb.customize [
        'modifyvm', :id,
        '--name', 'Zabbix Template for Varnish Cache (Varnish 6.0.x)',
      ]
    end

    machine.vm.provision :ansible, **ansible_config do |ansible|
      ansible.extra_vars['settings']['varnish-plus'] = {
        'version' => '60',
        'user' => ENV['VARNISH_PLUS_6_PACKAGECLOUD_USER'],
      }
    end

    machine.vm.network :private_network, ip: '192.168.100.171'
  end

  config.vm.define :v41 do |machine|
    machine.vm.provider :virtualbox do |vb|
      vb.customize [
        'modifyvm', :id,
        '--name', 'Zabbix Template for Varnish Cache (Varnish 4.1.x)',
      ]
    end

    machine.vm.provision :ansible, **ansible_config do |ansible|
      ansible.extra_vars['settings']['varnish-plus'] = {
        'version' => '41',
        'user' => ENV['VARNISH_PLUS_PACKAGECLOUD_USER'],
      }
    end

    machine.vm.network :private_network, ip: '192.168.100.172'
  end
end
