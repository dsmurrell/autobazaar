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
    local('scp -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r abc.json root@%s:~/OpenBazaar-Server/' % ip)
    local('scp -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r openbazaar_manager.conf root@%s:/etc/init/' % ip)
    with settings(host_string=ip, user = 'root'):
        with cd('/etc/init'):
            run('sudo chmod 644 openbazaar_manager.conf')

def add_store(ip, storename, username, password):
    with settings(host_string=ip, user = 'root'):
        with cd('~/OpenBazaar-Server'):
            run('python abc.py add %s %s %s' % (storename, username, password))

def remove_store(ip, storename):
    with settings(host_string=ip, user = 'root'):
        with cd('~/OpenBazaar-Server'):
            run('python abc.py remove %s' % storename)

def run_manager_service(ip):
    with settings(host_string=ip, user = 'root'):
        run('sudo service openbazaar_manager restart')

def stop_store(ip, storename):
    with settings(host_string=ip, user = 'root'):
        with cd('~/OpenBazaar-Server'):
            run('python manager.py stop %s' % storename)

def restart_store(ip, storename):
    with settings(host_string=ip, user = 'root'):
        with cd('~/OpenBazaar-Server'):
            run('python manager.py restart %s' % storename)

# read the config file
Config = ConfigParser.ConfigParser()
Config.read('ab.cfg')
digital_ocean_api_token = Config.get('MANDATORY', 'digital_ocean_api_token')
ssh_key = Config.get('MANDATORY', 'ssh_key')
droplet_name = Config.get('OPTIONAL', 'droplet_name')
droplet_region = Config.get('OPTIONAL', 'droplet_region')

# get hold of the arguments
parser = argparse.ArgumentParser()
parser.add_argument('-n', '--num-stores', default=4)
parser.add_argument('-u', '--username', default='onelove')
args = parser.parse_args()

print args.num_stores
print args.username

#ip = create_digital_ocean_droplet(digital_ocean_api_token, ssh_key, droplet_name, droplet_region)
#ip = '178.62.224.220'
ip = '178.62.228.167'
#install_openbazaar(ip)
copy_autobazaar_files(ip)
for i in range(1, args.num_stores+1):
    add_store(ip, 'ob%d' % i, args.username, generate_password(32))
run_manager_service(ip)

# ip = '178.62.236.199'
# copy_autobazaar_files(ip)
# add_store(ip, 'store_1', args.username, generate_password(32))
# run_autostart_service(ip)



#     print 'Oh Yeah! Finished installing and running OpenBazaar-Server.'
#     print 'Please point your OpenBazaar client at IP: %s, username: %s, password: %s' % (ip_address, username, password)
#     print 'This is done by using a regular install of OpenBazaar (found at www.openbazaar.org), and adding a new server configuration'
#     print 'In the OpenBazaar program go to (top right of screen) menu > default > + New Server'
#     print 'If you need to access your droplet, you can ssh in using \'ssh root@%s\'' % ip_address


# #ip = create_and_install_digitial_ocean(digital_ocean_api_token, ssh_key, droplet_name, droplet_region)

# ip = '188.166.19.231'
# print ip
# copy_autobazaar_files(ip)
# add_store(ip, 'purechimp', 'daniel', generate_password(32))
# add_store(ip, 'autobazaar', 'daniel', generate_password(32))
# add_store(ip, 'dan', 'daniel', generate_password(32))

# ip = '178.62.228.167'
# print ip
# install_openbazaar(ip)
# copy_autobazaar_files(ip)
# make_ob_cfg_template(ip)
# add_store(ip, 'ob1', 'onelove', generate_password(32))
# add_store(ip, 'ob2', 'onelove', generate_password(32))
# add_store(ip, 'ob3', 'onelove', generate_password(32))
# add_store(ip, 'ob4', 'onelove', generate_password(32))
# add_and_run_autostart_service(ip)



# add_store('188.166.19.231', 'purechimp', 'daniel', generate_password(32))
# add_store('188.166.19.231', 'autobazaar', 'daniel', generate_password(32))
# add_store('188.166.19.231', 'dan', 'daniel', generate_password(32))

#add_and_run_autostart_service('188.166.19.231')

#restart_store('188.166.19.231', 'autobazaar')

















