import sys
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

def add_store(storename, username, password):
    c = load_config()
    store_numbers = []
    store_names = []
    for sn, (storenumber, username, password) in c.iteritems():
        store_numbers.append(storenumber)
        store_names.append(sn)
    for n in range(1, 10): # max 9 stores per droplet
        if n not in store_numbers and storename not in store_names:
            c[storename] = (n, username, password)
            save_config(c)
            return True

    return False

def remove_store(storename):
    c = load_config()
    removed = c.pop(storename, None)
    return removed

if sys.argv[1] == 'add':
    add_store(sys.argv[2], sys.argv[3], sys.argv[4])

if sys.argv[1] == 'remove':
    remove_store(sys.argv[2])
