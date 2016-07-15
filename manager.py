from fabric.api import *
import sys
import time
from tempfile import mkstemp
from shutil import move
from os import remove, close
import json

def save_config(config_dict):
    with open('/root/OpenBazaar-Server/abc.json', 'w') as f:
        json.dump(config_dict, f)

def load_config():
    with open('/root/OpenBazaar-Server/abc.json', 'r') as f:
        try:
            config_dict = json.load(f)
        except:
            config_dict = {}
    return config_dict

def replace(path, pattern, subst):
    fh, temp_path = mkstemp()
    with open(temp_path,'w') as temp_file:
        with open(path) as file:
            for line in file:
                temp_file.write(line.replace(pattern, subst))
    close(fh)
    remove(path)
    move(temp_path, path)

def add_store(storename, username, password):
    c = load_config()
    store_numbers = []
    store_names = []
    for sn, (storenumber, un, pwd) in c.iteritems():
        store_numbers.append(storenumber)
        store_names.append(sn)
    for n in range(1, 10): # max 9 stores per droplet
        if n not in store_numbers and storename not in store_names:
            c[storename] = (n, username, password)
            local('cp /etc/init/openbazaar_manager.conf /etc/init/openbazaar_%d.conf' % n)
            replace('/etc/init/openbazaar_%d.conf' % n, 'exec python manager.py', 'exec python manager.py run %s' % storename)
            local('sudo chmod 644 /etc/init/openbazaar_%d.conf' % n)
            save_config(c)
            return True
    return False

def remove_store(storename):
    c = load_config()
    removed = c.pop(storename, None)
    if removed:
        save_config(c)
        local('rm /etc/init/openbazaar_%d.conf' % removed[0])
    return removed

def run_store(storename):
    abc = load_config()
    storenumber, username, password = abc[storename]
    with cd('~/OpenBazaar-Server'):
        local('cp ob_template.cfg ob.cfg')
        replace('ob.cfg', '#USERNAME = username', 'USERNAME = %s' % username)
        replace('ob.cfg', '#PASSWORD = password', 'PASSWORD = %s' % password)
        replace('ob.cfg', '#DATA_FOLDER = /path/to/OpenBazaar/', 'DATA_FOLDER = /root/stores/%s/' % storename)
        local('python openbazaard.py start -p 1111%d -r %d8469 -w %d8466 -b %d8470 --pidfile %s.pid -a 0.0.0.0' % (storenumber, storenumber, storenumber, storenumber, storename))

def restart_store(storename):
    abc = load_config()
    storenumber, username, password = abc[storename]
    local('sudo service openbazaar_%d restart' % storenumber)

def restart_all_stores():
    abc = load_config()
    for storename, (storenumber, username, password) in abc.iteritems():
        restart_store(storename)
        time.sleep(10)

def stop_store(storename):
    abc = load_config()
    storenumber, username, password = abc[storename]
    local('sudo service openbazaar_%d stop' % storenumber)

def stop_all_stores():
    abc = load_config()
    for storename, (storenumber, username, password) in abc.iteritems():
        stop_store(storename)

# no arguments restarts all the stores and keeps the manager running indefinitely
if len(sys.argv) == 1:
    print 'Started manager... restarting all stores...'
    restart_all_stores()
    while True:
        print 'manager running...'
        time.sleep(10)
if sys.argv[1] == 'restart_all':
    restart_all_stores()
elif sys.argv[1] == 'stop_all':
    stop_all_stores()
elif sys.argv[1] == 'run':
    run_store(sys.argv[2])
elif sys.argv[1] == 'restart':
    restart_store(sys.argv[2])
elif sys.argv[1] == 'stop':
    stop_store(sys.argv[2])
elif sys.argv[1] == 'add':
    add_store(sys.argv[2], sys.argv[3], sys.argv[4])
elif sys.argv[1] == 'remove':
    remove_store(sys.argv[2])

        



