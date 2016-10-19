import sys
import pip
import json
import time
import datetime
import argparse

pip.main(['install', 'python-digitalocean'])
pip.main(['install', 'fabric'])
pip.main(['install', 'configparser'])
pip.main(['install', 'ConfigParser'])

import digitalocean
from fabric.api import *
import configparser
from password import generate_password

# exit if python version 3
python_version = sys.version_info.major
if python_version == 3:
    import configparser
else:
    import ConfigParser


def create_digital_ocean_droplet(digital_ocean_api_token, ssh_key, droplet_name, droplet_region, output_filename):
    root_droplet_name = droplet_name
    manager = digitalocean.Manager(token=digital_ocean_api_token)

    def already_a_droplet_by_name():
        droplets = manager.get_all_droplets()
        for droplet in droplets:
            if droplet.name == droplet_name:
                return True
        return False

    count = 1
    while already_a_droplet_by_name():
        droplet_name = root_droplet_name + '-' + str(count)
        count += 1
            
    # # how to exit and note an issue
    # data = {'issue': 'Looks like you already have a droplet with the name: %s' % droplet_name}
    # with open(output_filename, 'w') as f:
    #     json.dump(data, f)
    # return sys.exit(1)

    droplet = digitalocean.Droplet(token=digital_ocean_api_token,
                                   name=droplet_name,
                                   region=droplet_region, 
                                   ssh_keys=[ssh_key],
                                   #image='ubuntu-14-04-x64',
                                   image='ubuntu-16-04-x64', 
                                   size_slug='512mb',  
                                   backups=False)

    print('Creating OpenBazaar-Server droplet on Digital Ocean.')
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
            for i in range(30):
                time.sleep(1)
                sys.stdout.write('.'); sys.stdout.flush()
            print('')
            break
    print('OpenBazaar-Server droplet created with IP: ' + droplet.ip_address)
    return droplet.ip_address

def install_openbazaar(ip):
    print('Installing OpenBazaar-Server and dependencies')
    with settings(host_string=ip, user = 'root'):

        # ubuntu 14-04
        # run('sudo add-apt-repository -y ppa:chris-lea/libsodium')
        # run('sudo apt-get update')
        # run('sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" dist-upgrade')
        # run('sudo apt-get install -y git build-essential libssl-dev libffi-dev python-dev openssl python-pip autoconf pkg-config libtool libzmq3-dev libsodium-dev')
        # run('sudo pip install cryptography')
        # run('git clone https://github.com/zeromq/libzmq')
        # with cd('~/libzmq'):
        #     run('./autogen.sh && ./configure && make -j 4')
        #     run('make check && make install && sudo ldconfig')
        # run('git clone https://github.com/OpenBazaar/OpenBazaar-Server.git')
        # with cd('~/OpenBazaar-Server'):
        #     run('sudo pip install -r requirements.txt')
        #     run('sudo pip install fabric')

        # ubuntu 16-04
        run('sudo apt-get update -y && sudo apt-get upgrade -y')
        run('sudo apt-get install -y git build-essential libssl-dev libffi-dev python-dev openssl python-pip libsodium-dev autoconf libzmq-dev pkg-config libtool')
        run('sudo apt-get install -y libzmq3-dev')
        run('pip install --upgrade pip')
        run('sudo pip install cryptography')
        run('sudo git clone https://github.com/OpenBazaar/OpenBazaar-Server.git')
        run('sudo pip install fabric')
        with cd('~/OpenBazaar-Server'):
            run('sudo pip install -r requirements.txt')

    sys.stdout.write('\nWaiting again for network services .')
    for i in range(10):
        time.sleep(1)
        sys.stdout.write('.'); sys.stdout.flush()
    print('')

def copy_autobazaar_files(ip):
    local('scp -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r manager.py root@%s:~/OpenBazaar-Server/' % ip)
    local('scp -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r ob_template.cfg root@%s:~/OpenBazaar-Server/' % ip)
    local('scp -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r abc.json root@%s:~/OpenBazaar-Server/' % ip)
    local('scp -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r openbazaar.conf root@%s:/etc/init/' % ip)
    with settings(host_string=ip, user = 'root', warn_only=True):
        with cd('~'):
            run('mkdir logs')
        with cd('/etc/init'):
            run('sudo chmod 644 openbazaar.conf')

def copy_autobazaar_files_without_config_dict(ip):
    local('scp -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r manager.py root@%s:~/OpenBazaar-Server/' % ip)
    local('scp -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r ob_template.cfg root@%s:~/OpenBazaar-Server/' % ip)
    local('scp -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r openbazaar.conf root@%s:/etc/init/' % ip)
    with settings(host_string=ip, user = 'root', warn_only=True):
        with cd('~'):
            run('mkdir logs')
        with cd('/etc/init'):
            run('sudo chmod 644 openbazaar.conf')

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

def spawn_manage(ip):
    with settings(host_string=ip, user = 'root'):
        with cd('~/OpenBazaar-Server'):
            run('python manager.py spawn_manage')

def setup_server(ip, username, num_stores, output_filename):
    install_openbazaar(ip)
    copy_autobazaar_files(ip)
    passwords = []
    for i in range(1, args.num_stores+1):
        passwords.append(generate_password(32))
        add_store(ip, 'store_%d' % i, args.username, passwords[i-1])
    spawn_manage(ip)

    # create and write output file
    data = {}
    data['ip'] = ip
    data['username'] = username
    for i in range(args.num_stores):
        num = i+1
        data[num] = {}
        data[num]['password'] = passwords[i]
        data[num]['rest'] = str(num) + '8469'
        data[num]['websocket'] = str(num) + '8466'
        data[num]['heartbeat'] = str(num) + '8470'
    with open(output_filename, 'w') as f:
        json.dump(data, f)

    print('Oh Yeah! Finished installing and running your OpenBazaar stores.')
    print('If you restart your droplet all your stores will respawn.')
    print('Now you can connect OpenBazaar (found at www.openbazaar.org) to your stores in the cloud by adding new server configurations as follows:')
    print('In the OpenBazaar program go to menu (top right of screen) -> default -> + New Server\n')
    for i in range(args.num_stores):
        num = i+1
        print('For store #%d, please use the following configurations options:' % num)
        hap = str(num) + '8469'
        wap = str(num) + '8466'
        hsp = str(num) + '8470'
        print('\tServer IP: %s\n\tUsername: %s\n\tPassword: %s\n\tRest API Port: %s\n\tWebsocket API port: %s\n\tHeartbeat socket port: %s\n' % (ip, username, passwords[i], hap, wap, hsp))
    print('If you need to access your droplet to make any changes manually, you can ssh in using \'ssh root@%s\'' % ip)

def setup_digital_ocean_droplet(digital_ocean_api_token, ssh_key, droplet_name, droplet_region, username, num_stores, output_filename):
    print('Creating %d stores on a Digital Ocean droplet.' % num_stores)
    ip = create_digital_ocean_droplet(digital_ocean_api_token, ssh_key, droplet_name, droplet_region, output_filename)
    if ip:
        setup_server(ip, username, num_stores, output_filename)

# get hold of the arguments
parser = argparse.ArgumentParser()
parser.add_argument('-u', '--username', default='user')
parser.add_argument('-n', '--num-stores', type=int, default=1, choices=range(1, 6))
parser.add_argument('-hs', '--hosting-service', default='DigitalOcean', choices=['None', 'DigitalOcean'])
parser.add_argument('-ip', '--ip-address', default='None')
parser.add_argument('-o', '--output-filename', default='output.json')
parser.add_argument('-t', '--api-token', default='None')
parser.add_argument('-spk', '--ssh-public-key', default='None')
args = parser.parse_args()

if args.hosting_service == 'None':
    setup_server(args.ip_address, args.username, args.num_stores)

elif args.hosting_service == 'DigitalOcean':
    Config = configparser.ConfigParser()
    Config.read('ab.cfg')
    if args.api_token == 'None':
        digital_ocean_api_token = Config.get('MANDATORY', 'digital_ocean_api_token')
    else:
        digital_ocean_api_token = args.api_token 
    if args.ssh_public_key == 'None':
        ssh_key = Config.get('MANDATORY', 'ssh_key')
    else:
        ssh_key = args.ssh_public_key
    droplet_name = Config.get('OPTIONAL', 'droplet_name')
    droplet_region = Config.get('OPTIONAL', 'droplet_region')
    setup_digital_ocean_droplet(digital_ocean_api_token, ssh_key, droplet_name, droplet_region, args.username, args.num_stores, args.output_filename)





















