from fabric.api import *
import sys

with cd('~/OpenBazaar-Server'):
    local('echo \'logfile manager.log\' > ~/.screenrc')
    local('screen -d -m -S manager -L python manager.py; sleep 2')