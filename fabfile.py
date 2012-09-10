# coding=utf-8
import os
from fabric.api import *
from fabric.colors import *
from fabric.contrib.files import exists
from datetime import datetime

LOCAL_TEMP_FOLDER = '/tmp'
REPO_URL = 'https://github.com/Topface/analystics.git'
REMOTE_APP_FOLDER = '/home/analystics/'

env.roledefs = {
    'dev': ['analystics@192.168.2.103'],
    'prod': []
}

# qqqwwweee

@roles('prod', 'dev')
def deploy():
    print(green("Start deploy analystics on {0}".format(env.host_string)))

    now = datetime.now()
    time = now.time()
    date = now.date()
    server_folder = 'server_{0}_{1}_{2}_{3}_{4}_{5}'.format(date.year, date.month, date.day, time.hour, time.minute, time.second)

    if os.path.exists(LOCAL_TEMP_FOLDER + '/analystics_server'):
        print(white('remove ' + LOCAL_TEMP_FOLDER + '/analystics_server'))
        local('rm -rf ' + LOCAL_TEMP_FOLDER + '/analystics_server')

    local('git clone ' + REPO_URL + ' ' + LOCAL_TEMP_FOLDER + '/analystics_server')
    if os.path.exists('analystics_server.tar.gz'):
        print(white('remove analystics_server.tar.gz'))
        local('rm -rf analystics_server.tar.gz')

    local('tar -pczf analystics_server.tar.gz ' + LOCAL_TEMP_FOLDER + '/analystics_server/server')
    put('analystics_server.tar.gz', '/home/analystics/')
    local('rm analystics_server.tar.gz')
    isFirst = False

    with cd(REMOTE_APP_FOLDER):
        run('tar xzf analystics_server.tar.gz')
        run('rm analystics_server.tar.gz')
        # copy to deploy folder
        if not exists('deploy'):
            run('mkdir deploy')
            isFirst = True

        run('mv tmp/analystics_server/server deploy/' + server_folder)

        run('rm -rf tmp ')
        if not isFirst:
            stopServer()
        run('rm -rf server ')
        run('ln -f -s deploy/' + server_folder + ' server')
        run('chmod a+x server/runServer.py')

        startServer()
        if isFirst:
            print(yellow('please, configure project manualy at first run'))
        else:
            updateMySQL()
            restartNginx()

def stopServer():
    run('sudo server/runServer.py stop')

def startServer():
    run('sudo server/runServer.py start')

def restartNginx():
    run('sudo /usr/sbin/nginx -s reload')

def updateMySQL():
    '''
    call mysql migration script
    '''
    with cd(REMOTE_APP_FOLDER):
        run('chmod a+x server/updateDB.py')
        run('sudo server/updateDB.py')






