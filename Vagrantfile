# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure('2') do |config|
  config.vm.box = 'ubuntu/trusty64'
  config.vm.box_version = '=14.04'
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
    ]
  end

  config.vm.define :v50 do |machine|
    machine.vm.hostname = 'dev'

    machine.vm.provider :virtualbox do |vb|
      vb.customize [
        'modifyvm', :id,
        '--name', 'Zabbix Template for Varnish Cache (Varnish 5.0.x)',
      ]
    end

    machine.vm.synced_folder 'extras/envs/dev/ansible', '/srv/ansible', :nfs => false
    machine.vm.provision 'ansible', type: 'ansible_local' do |ansible|
      ansible.playbook = '/srv/ansible/playbook.yml'
      ansible.verbose = 'v'
      ansible.extra_vars = {
        'settings' => {
          'mysql.root' => {
            'password' => 's3cr3t',
          },
          'mysql.zabbix' => {
            'name' => 'zabbix',
            'user' => 'zabbix',
            'password' => 'zabbix',
          },
        }
      }
      ansible.install_mode = 'pip'
      ansible.version = '2.6.4'
    end

    machine.vm.network :public_network
    machine.vm.network :private_network, ip: '192.168.100.172'

    machine.vm.synced_folder '.', '/vagrant', :nfs => false
  end
end
