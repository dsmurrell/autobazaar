from fabric.api import *
import sys
import json
from manager import replace

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

if sys.argv[1] == 'add':
    add_store(sys.argv[2], sys.argv[3], sys.argv[4])

if sys.argv[1] == 'remove':
    remove_store(sys.argv[2])
