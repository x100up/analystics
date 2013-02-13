# coding=utf-8
__author__ = 'pavlenko.roman.spb@gmail.com'
from models.Config import Config
from components.webhdfs import WebHDFS
import os, inspect
from datetime import datetime

# set configurations
rootPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory

config = Config()
config.readConfigFile(os.path.abspath(os.path.abspath(rootPath + '/../server.cfg')))

STATISTICS_ROOT = config.get('hdfs_statistic_path') + 'topface/'
HDFS_HOST = config.get('hdfs_host')
HDFS_PORT = int(config.get('hdfs_port'))
HDFS_USER = config.get('hdfs_username')
webHDFS = WebHDFS(HDFS_HOST, HDFS_PORT, HDFS_USER)

dirs = webHDFS.listdir(STATISTICS_ROOT)

def scanDir(dirname, eventcode, skip):
    years = webHDFS.listdir(dirname)
    for year in years:
        months = webHDFS.listdir(dirname + '/' + year)
        for month in months:
            days = webHDFS.listdir(dirname + '/' + year + '/' + month)
            for day in days:
                if (int(year), int(month), int(day)) in skip:
                    continue

                files = webHDFS.listdir(dirname + '/' + year + '/' + month + '/' + day)
                for filename in files:
                    if not filename.endswith('.snappy'):
                        print './packer.py -k{} -y{} -m{} -d{}'.format(eventcode, year, month, day)
                        break


now = datetime.now()

for directory in dirs:
    scanDir(STATISTICS_ROOT + directory, directory, [(now.year, now.month, now.day)])