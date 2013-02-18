#!/usr/bin/env python

import imp
import os
import subprocess
import sys

try:
    from msvcrt import getch
except ImportError:
    def getch():
        pass

# 
# Robot source files and directories
#

files = [
    'robot.py',
]

dirs = [
    'autonomous',
    'common',
    'components',
    'systems',
]


def relpath(path):
    '''Path helper, gives you a path relative to this file'''
    return os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), path))


if __name__ == '__main__':
    
    #
    # simple test before sending it out, in case of simple errors
    #
    
    print('Importing robot.py...')
    
    if sys.platform == 'win32':
        ret = subprocess.call([relpath('../run_test.bat'), 'import_test', '--robot-path', relpath('.')], shell=True)
    else:
        ret = subprocess.call([relpath('../run_test.sh'), 'import_test', '--robot-path', relpath('.')], shell=True)
        
    if ret != 0:
        print("Failure detected, aborting import")
        exit(1)
        
    
    print('Import successful!')
    
    
    #
    # Ok, load the installer now
    #
    
    
    try:
        installer = imp.load_source('install', relpath('../../robotpy/install.py'))
    except IOError as e:
        print("Error loading the RobotPy installer library! (%s)\n\n" % e)
        getch()
        exit(1)
        
    robot_host = '10.24.23.2'
        
    print('Connecting to robot host %s' % robot_host)
    
    try:
        server = installer.RobotCodeInstaller(robot_host)
    except Exception as e:
        print("Error connecting to remote host: %s" % e)
        getch()
        exit(1)
    
    local_root = os.path.dirname(__file__)
    
    
    print('Beginning upload.')
    
    remote_root = '/py'
    
    # wipe the whole thing, to ensure that we don't have any cruft lying around
    server.delete_remote(remote_root)
    server.create_remote_directory(remote_root)
    
    # restore boot.py
    server.upload_file(remote_root, relpath('../../robotpy'), 'boot.py')
    
    for file in files:
        server.upload_file(remote_root, local_root, file)
        
    for dir in dirs:
        server.upload_directory(remote_root + '/' + dir, os.path.join(local_root, dir), verbose=True)
    
    print('Upload complete.')
    
    # close the installer
    server.close()
    
    # ask the user to reboot after installation?
    while True:
        if sys.version_info[0] < 3:
            yn = str(raw_input("Reboot robot? [y/n]")).strip().lower()
        else:
            yn = str(input("Reboot robot? [y/n]")).strip().lower()
            
        if yn == 'y':
            installer.reboot_crio()
            break
        elif yn == 'n':
            break
