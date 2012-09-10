# coding=utf-8
import os
from fabric.api import *
from fabric.colors import *
from fabric.contrib.files import exists
from datetime import datetime
env.hosts = ['analystics@192.168.2.103']
# qqqwwweee


def deploy():
    print(green("Start deploy analystics server"))

    now = datetime.now()
    time = now.time()
    date = now.date()
    server_folder = 'server_{0}_{1}_{2}_{3}_{4}_{5}'.format(date.year, date.month, date.day, time.hour, time.minute, time.second)

    if os.path.exists('/tmp/analystics_server'):
        print(white('remove /tmp/analystics_server'))
        local('rm -rf /tmp/analystics_server')

    local('git clone https://github.com/Topface/analystics.git /tmp/analystics_server')
    if os.path.exists('analystics_server.tar.gz'):
        print(white('remove analystics_server.tar.gz'))
        local('rm -rf analystics_server.tar.gz')

    local('tar -pczf analystics_server.tar.gz /tmp/analystics_server/server')
    put('analystics_server.tar.gz', '/home/analystics/')
    local('rm analystics_server.tar.gz')
    isFirst = False

    with cd('/home/analystics/'):
        run('tar xzf analystics_server.tar.gz ')
        run('rm analystics_server.tar.gz ')
        # copy to deploy folder
        if not exists('deploy'):
            run('mkdir deploy')
            isFirst = True

        run('mv tmp/analystics_server/server deploy/' + server_folder)

        run('rm -rf tmp ')
        run('ln -sf deploy/' + server_folder + ' server')

    # restart tornado
    with cd('/home/analystics/server'):
        if isFirst:
            sudo('python runServer.py start')
        else:
            sudo('python runServer.py stop')
            sudo('python runServer.py start')



    # restart nginx
    run('nginx -s reload')





