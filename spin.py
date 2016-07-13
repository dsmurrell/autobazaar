import sys, time
import digitalocean
from fabric.api import *
import datetime
import ConfigParser
from password import generate_password

# read the config file
Config = ConfigParser.ConfigParser()
Config.read('ab.cfg')
digital_ocean_api_token = Config.get('MANDATORY', 'digital_ocean_api_token')
ssh_key = Config.get('MANDATORY', 'ssh_key')
username = Config.get('MANDATORY', 'username')
droplet_name = Config.get('OPTIONAL', 'droplet_name')
droplet_region = Config.get('OPTIONAL', 'droplet_region')
# generate random password
password = generate_password(32)

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

def install_openbazaar(IP):
    print 'Installing OpenBazaar-Server and dependencies'
    with settings(host_string=IP, user = 'root'):

        run('sudo add-apt-repository -y ppa:chris-lea/libsodium')
        run('sudo apt-get update && sudo apt-get -y upgrade')
        run('sudo apt-get install -y git build-essential libssl-dev libffi-dev python-dev openssl python-pip autoconf pkg-config libtool libzmq3-dev libsodium-dev')
        run('sudo pip install cryptography')
        run('git clone https://github.com/zeromq/libzmq')
        with cd('~/libzmq'):
            run('./autogen.sh && ./configure && make -j 4')
            run('make check && make install && sudo ldconfig')
        run('git clone https://github.com/OpenBazaar/OpenBazaar-Server.git')
        with cd('~/OpenBazaar-Server'):
            run('sudo pip install -r requirements.txt')

    sys.stdout.write('\nWaiting again for network services .')
    for i in range(10):
        time.sleep(1)
        sys.stdout.write('.'); sys.stdout.flush()
    print ''

def change_username_and_password(IP, username, password):
    local('scp -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r add_user_pass.py root@%s:~/OpenBazaar-Server/' % IP)
    with settings(host_string=IP, user = 'root'):
        with cd('~/OpenBazaar-Server'):
            run('python add_user_pass.py %s %s' % (username, password))

def add_autostart_service(IP):
    local('scp -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r openbazaar.conf root@%s:/etc/init/' % IP)
    with settings(host_string=IP, user = 'root'):
        with cd('/etc/init'):
            run('sudo chmod 644 openbazaar.conf')
            run('sudo service openbazaar start')

def create_and_install_digitial_ocean():
    start_time = datetime.datetime.now()
    ip_address = create_digital_ocean_droplet(digital_ocean_api_token, ssh_key, droplet_name, droplet_region)
    install_openbazaar(ip_address)
    change_username_and_password(ip_address, username, password)
    add_autostart_service(ip_address)
    print 'Oh Yeah! Finished installing and running OpenBazaar-Server.'
    end_time = datetime.datetime.now()
    print 'Finished in %d seconds.' % (end_time-start_time).total_seconds()
    print 'Please point your OpenBazaar client at IP: %s, username: %s, password: %s' % (ip_address, username, password)
    print 'This is done by using a regular install of OpenBazaar (found at www.openbazaar.org), and adding a new server configuration'
    print 'In the OpenBazaar program go to (top right of screen) menu > default > + New Server'
    print 'If you need to access your droplet, you can ssh in using \'ssh root@%s\'' % ip_address

create_and_install_digitial_ocean()













