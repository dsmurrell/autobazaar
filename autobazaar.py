import sys, time
import digitalocean
from fabric.api import *
import datetime
import ConfigParser
from password import generate_password
import json
import argparse

def create_digital_ocean_droplet(digital_ocean_api_token, ssh_key, droplet_name, droplet_region):
    manager = digitalocean.Manager(token=digital_ocean_api_token)
    droplets = manager.get_all_droplets()
    for droplet in droplets:
        if droplet.name == droplet_name:
            print 'You already have droplet with name: %s, Shutting down.' % droplet_name
            return False

    droplet = digitalocean.Droplet(token=digital_ocean_api_token,
                                   name=droplet_name,
                                   region=droplet_region, 
                                   ssh_keys=[ssh_key],
                                   image='ubuntu-14-04-x64', 
                                   size_slug='512mb',  
                                   backups=False)

    print 'Creating OpenBazaar-Server droplet on Digital Ocean.'
    droplet.create()

    # check on the status of the droplet and wait for it to become available
    status = 'in-progress'
    sys.stdout.write('Waiting for droplet to be created .')
    while True:
        sys.stdout.write('.'); sys.stdout.flush()
        actions = droplet.get_actions()
        for action in actions:
            action.load()
            status = action.status
        if status == 'completed':
            droplet.load()
            sys.stdout.write('\nWaiting for network services to become available .')
            for i in range(20):
                time.sleep(1)
                sys.stdout.write('.'); sys.stdout.flush()
            print ''
            break
    print 'OpenBazaar-Server droplet created with IP: ' + droplet.ip_address
    return droplet.ip_address

def install_openbazaar(ip):
    print 'Installing OpenBazaar-Server and dependencies'
    with settings(host_string=ip, user = 'root'):

        run('sudo add-apt-repository -y ppa:chris-lea/libsodium')
        run('sudo apt-get update')
        run('sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" dist-upgrade')
        run('sudo apt-get install -y git build-essential libssl-dev libffi-dev python-dev openssl python-pip autoconf pkg-config libtool libzmq3-dev libsodium-dev')
        run('sudo pip install cryptography')
        run('git clone https://github.com/zeromq/libzmq')
        with cd('~/libzmq'):
            run('./autogen.sh && ./configure && make -j 4')
            run('make check && make install && sudo ldconfig')
        run('git clone https://github.com/OpenBazaar/OpenBazaar-Server.git')
        with cd('~/OpenBazaar-Server'):
            run('sudo pip install -r requirements.txt')
            run('sudo pip install fabric')

    sys.stdout.write('\nWaiting again for network services .')
    for i in range(10):
        time.sleep(1)
        sys.stdout.write('.'); sys.stdout.flush()
    print ''

def copy_autobazaar_files(ip):
    local('scp -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r manager.py root@%s:~/OpenBazaar-Server/' % ip)
    local('scp -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r ob_template.cfg root@%s:~/OpenBazaar-Server/' % ip)
    local('scp -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r openbazaar_upstart root@%s:/etc/init/' % ip)
    local('scp -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r abc.json root@%s:~/OpenBazaar-Server/' % ip)

def copy_autobazaar_files_without_config_dict(ip):
    local('scp -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r manager.py root@%s:~/OpenBazaar-Server/' % ip)
    local('scp -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r ob_template.cfg root@%s:~/OpenBazaar-Server/' % ip)
    local('scp -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r openbazaar_upstart root@%s:/etc/init/' % ip)

def add_store(ip, storename, username, password):
    with settings(host_string=ip, user = 'root'):
        with cd('~/OpenBazaar-Server'):
            run('python manager.py add %s %s %s' % (storename, username, password))

def remove_store(ip, storename):
    with settings(host_string=ip, user = 'root'):
        with cd('~/OpenBazaar-Server'):
            run('python manager.py remove %s' % storename)

def remove_all_stores(ip):
    stop_all_stores(ip)
    with settings(host_string=ip, user = 'root'):
        with cd('~/OpenBazaar-Server'):
            run('python manager.py remove_all')

def restart_store(ip, storename):
    with settings(host_string=ip, user = 'root'):
        with cd('~/OpenBazaar-Server'):
            run('python manager.py restart %s' % storename)

def restart_all_stores(ip):
    with settings(host_string=ip, user = 'root'):
        with cd('~/OpenBazaar-Server'):
            run('python manager.py restart_all')

def stop_store(ip, storename):
    with settings(host_string=ip, user = 'root'):
        with cd('~/OpenBazaar-Server'):
            run('python manager.py stop %s' % storename)

def stop_all_stores(ip):
    with settings(host_string=ip, user = 'root'):
        with cd('~/OpenBazaar-Server'):
            run('python manager.py stop_all')

def delete_all_logs(ip):
    with settings(host_string=ip, user = 'root'):
        with cd('~/OpenBazaar-Server'):
            run('python manager.py delete_all_logs')

# read the config file
Config = ConfigParser.ConfigParser()
Config.read('ab.cfg')
digital_ocean_api_token = Config.get('MANDATORY', 'digital_ocean_api_token')
ssh_key = Config.get('MANDATORY', 'ssh_key')
droplet_name = Config.get('OPTIONAL', 'droplet_name')
droplet_region = Config.get('OPTIONAL', 'droplet_region')

# get hold of the arguments
parser = argparse.ArgumentParser()
parser.add_argument('-u', '--username', default='user')
parser.add_argument('-n', '--num-stores', default=3)
args = parser.parse_args()
args.num_stores = int(args.num_stores)
print 'Creating %d stores on a Digital Ocean droplet with username: %s.' % (args.num_stores, args.username)

def setup_digital_ocean_droplet(digital_ocean_api_token, ssh_key, droplet_name, droplet_region, username, num_stores):
    ip = create_digital_ocean_droplet(digital_ocean_api_token, ssh_key, droplet_name, droplet_region)
    install_openbazaar(ip)
    copy_autobazaar_files(ip)
    for i in range(1, args.num_stores+1):
        add_store(ip, 'store_%d' % i, args.username, generate_password(32))
    restart_all_stores(ip)

setup_digital_ocean_droplet(digital_ocean_api_token, ssh_key, droplet_name, droplet_region, args.username, args.num_stores)

















