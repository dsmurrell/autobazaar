from fabric.api import *
import sys
import time
from tempfile import mkstemp
from shutil import move
from os import remove, close
import json
import twisted.internet
from twisted.internet import reactor, task
from subprocess import check_output

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
    for n in range(1, 6): # max 5 stores per droplet (the port range goes out of bounds with 6)
        if n not in store_numbers and storename not in store_names:
            c[storename] = (n, username, password)
            save_config(c)
            return True
    return False

def remove_store(storename):
    c = load_config()
    removed = c.pop(storename, None)
    if removed:
        save_config(c)
    return removed

def remove_all_stores():
    abc = load_config()
    for storename, (storenumber, username, password) in abc.iteritems():
        remove_store(storename)

def restart_store(storename):
    print 'Restarting store %s.' % storename
    abc = load_config()
    storenumber, username, password = abc[storename]
    with cd('~/OpenBazaar-Server'):
        local('cp ob_template.cfg ob.cfg')
        replace('ob.cfg', '#USERNAME = username', 'USERNAME = %s' % username)
        replace('ob.cfg', '#PASSWORD = password', 'PASSWORD = %s' % password)
        replace('ob.cfg', '#DATA_FOLDER = /path/to/OpenBazaar/', 'DATA_FOLDER = /root/stores/%s/' % storename)
        try:
            local("screen -S %s -X stuff $'\003'" % storename)
            time.sleep(10)
        except:
            pass
        local('echo \'logfile ../logs/%s.log\' > ~/.screenrc' % storename)
        local('screen -d -m -S %s -L python openbazaard.py start -p 1111%d -r %d8469 -w %d8466 -b %d8470 --pidfile %s.pid -a 0.0.0.0; sleep 1' % (storename, storenumber, storenumber, storenumber, storenumber, storename))

def restart_all_stores():
    abc = load_config()
    for storename, (storenumber, username, password) in abc.iteritems():
        restart_store(storename)

def stop_store(storename):
    abc = load_config()
    storenumber, username, password = abc[storename]
    try:
        local("screen -S %s -X stuff $'\003'" % storename)
        time.sleep(10)
    except:
        pass

def stop_all_stores():
    abc = load_config()
    for storename, (storenumber, username, password) in abc.iteritems():
        stop_store(storename)

def delete_all_logs():
    abc = load_config()
    for storename, (storenumber, username, password) in abc.iteritems():
        with settings(warn_only=True):
            with cd('~/logs'):
                local('rm %s.log' % storename)

def screen_running(name):
        var = check_output(["screen -ls; true"],shell=True)
        if "."+name+"\t(" in var:
            return True
        else:
            return False

def maintain():
    abc = load_config()
    for storename in abc.keys():
        if not screen_running(storename):
            print 'Store %s went down... restarting...' % storename
            restart_store(storename)

def loop_restart_store(storename, interval):
    print 'loop restart store: %s, %s' % (storename, interval)
    task.LoopingCall(restart_store, storename).start(interval)

def manage():
    print 'Started manager... restarting all stores.'
    restart_all_stores()

    # handle the restarting of stores
    abc = load_config()
    interval = 3600 # 1 hour in seconds
    int_frac = interval / len(abc)
    for i, storename in enumerate(abc.keys()):
        reactor.callLater((i * int_frac) + int_frac, loop_restart_store, storename, interval)

    # restart stores that have gone down
    task.LoopingCall(maintain).start(5, now=False)
    twisted.internet.reactor.run()

# do something based on the command line arguments
if sys.argv[1] == 'spawn_manage':
    with settings(warn_only=True):
        with cd('~/OpenBazaar-Server'):
            local('screen -X -S manage quit')
            local('echo \'logfile ../logs/manage.log\' > ~/.screenrc')
            local('screen -d -m -S manage -L python manager.py manage; sleep 1')
if sys.argv[1] == 'manage':
    manage()
elif sys.argv[1] == 'add':
    add_store(sys.argv[2], sys.argv[3], sys.argv[4])
elif sys.argv[1] == 'remove':
    remove_store(sys.argv[2])
elif sys.argv[1] == 'restart':
    restart_store(sys.argv[2])
elif sys.argv[1] == 'stop':
    stop_store(sys.argv[2])
elif sys.argv[1] == 'restart_all':
    restart_all_stores()
elif sys.argv[1] == 'stop_all':
    stop_all_stores()
elif sys.argv[1] == 'delete_all_logs':
    delete_all_logs()
elif sys.argv[1] == 'remove_all':
    remove_all_stores()

        



