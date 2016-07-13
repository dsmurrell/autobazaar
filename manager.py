from fabric.api import *
import sys
import time
from tempfile import mkstemp
from shutil import move
from os import remove, close
import json

def load_config():
    with open('/root/OpenBazaar-Server/abc.json', 'r') as f:
        try:
            config_dict = json.load(f)
        except:
            config_dict = {}
    return config_dict

def replace(source_path, dest_path, pattern, subst):
    fh, temp_path = mkstemp()
    with open(temp_path,'w') as temp_file:
        with open(source_path) as source_file:
            for line in source_file:
                temp_file.write(line.replace(pattern, subst))
    close(fh)
    remove(dest_path)
    move(temp_path, dest_path)

def relaunch_store(storename):
    abc = load_config()
    storenumber, username, password = abc['storename']
    with cd('~/OpenBazaar-Server'):
        print 'Stopping store %s.' % storename
        local("screen -S %s -X stuff $'\003'" % storename)
        time.sleep(10)
        print 'Starting store %s.' % storename
        replace('ob_template.cfg', 'ob.cfg', '#USERNAME = username', 'USERNAME = %s' % username)
        replace('ob_template.cfg', 'ob.cfg', '#PASSWORD = password', 'PASSWORD = %s' % password)
        replace('ob_template.cfg', 'ob.cfg', '#DATA_FOLDER = /path/to/OpenBazaar/', 'DATA_FOLDER = /root/stores/%s/' % storename)

        local('echo \'logfile %s.log\' > ~/.screenrc' % storename)
        local('screen -d -m -S %s -L python openbazaard.py start -p 1111%d -r %d8469 -w %d8466 -b %d8470 --pidfile %s.pid -a 0.0.0.0; sleep 1' % (storename, storenumber, storenumber, storenumber, storenumber, storename))

def relaunch_all_stores():
    abc = load_config()
    for storename, (storenumber, username, password) in abc.iteritems():
        print storename, storenumber, username, password
        relaunch_store(storename)


if sys.argv[1] == 'relaunch':

else:

if len(sys.argv) == 1:
    with settings(warn_only=True):
        print 'Started manager... restarting all stores.'
        relaunch_all_stores()
        abc = load_config()
        total_time = 21600 # 6 hours in seconds
        one_time = total_time / len(abc)
        while True:
            for storename, (storenumber, username, password) in abc.iteritems():
                time.sleep(one_time)
                relaunch_store(storename)
else:
    if sys.argv[1] == 'relaunch':
        



