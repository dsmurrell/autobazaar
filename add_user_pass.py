from tempfile import mkstemp
from shutil import move
from os import remove, close
import sys

def replace(file_path, pattern, subst):
    fh, abs_path = mkstemp()
    with open(abs_path,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    close(fh)
    remove(file_path)
    move(abs_path, file_path)

replace('ob.cfg', '#USERNAME = username', 'USERNAME = ' + sys.argv[1])
replace('ob.cfg', '#PASSWORD = password', 'PASSWORD = ' + sys.argv[2])