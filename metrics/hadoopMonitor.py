#!/usr/bin/python
# coding=utf-8
__author__ = 'pavlenko.roman.spb@gmail.com'

import json
import os
import inspect
import ConfigParser
import urllib2

class DataProcessor():
    path = '/tmp/hadoop_meterics/'

    def write(self, data, prefix = ''):
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        for k in data:
            f = open(self.path + prefix + k + '.metrics', 'w')
            f.write(str(data[k]))
            f.close()
            os.chmod(self.path + prefix + k + '.metrics', 0664)




class FlumeDataProcessor(DataProcessor):

    def process(self, url):

        req = urllib2.Request(url)
        opener = urllib2.build_opener()
        f = opener.open(req)
        data = json.loads(f.read())

        ChannelFillPercentages = []
        EventPutAttemptCounts = []
        EventPutSuccessCounts = []
        ConnectionFailedCounts = []

        for key in data:
            channelData = data[key]
            if key.startswith('CHANNEL'):
                ChannelFillPercentages.append(float(channelData['ChannelFillPercentage']))
                EventPutAttemptCounts.append(float(channelData['EventPutAttemptCount']))
                EventPutSuccessCounts.append(float(channelData['EventPutSuccessCount']))

            if key.startswith('SINK'):
                ConnectionFailedCounts.append(float(channelData['ConnectionFailedCount']))

        # ключи файлы - значения
        result  = {
            'avgChannelFill': 0,
            'maxChannelFill': max(ChannelFillPercentages),
            'eventPutCount': sum(EventPutAttemptCounts),
            'eventPutSuccessCount': sum(EventPutSuccessCounts),
            'connectionFailedCount': sum(ConnectionFailedCounts)
        }

        _c = len(ChannelFillPercentages)
        if _c:
            result['avgChannelFill'] = sum(ChannelFillPercentages) / _c

        self.write(result, prefix='flume.')


class HadoopJMXDataProcessor(DataProcessor):

    def process(self, url):
        req = urllib2.Request(url)
        opener = urllib2.build_opener()
        f = opener.open(req)
        data = json.loads(f.read())

        result = {
            "CapacityTotal" : 0,
            "CapacityUsed" : 0,
            "CapacityRemaining" : 0,
            "TotalLoad" : 0,
            "BlocksTotal" : 0,
            "FilesTotal" : 0,
            "PendingReplicationBlocks" : 0,
            "UnderReplicatedBlocks" : 0,
            "ScheduledReplicationBlocks" : 0,
            "NumLiveDataNodes" : 0,
            "NumDeadDataNodes" : 0
        }

        for i in data['beans']:
            if i.has_key('name') and i['name'] == 'Hadoop:service=NameNode,name=FSNamesystemState':
                for k in result:
                    if i.has_key(k):
                        result[k] = i[k]

        self.write(result, prefix = 'hadoop.nn.')

thisPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory
root = os.path.abspath(thisPath)

configParser = ConfigParser.RawConfigParser()
configParser.read(root + '/metrics.cfg')
sections = configParser.sections()
config = {}
for section in sections:
    items = configParser.items(section)
    config[section] = {}
    for k, v in items:
        config[section][k] = v


if config.has_key('flume') and config['flume'].has_key('http'):
    print 'run flume metrics'
    flumeDataProcessor = FlumeDataProcessor()
    flumeDataProcessor.process(config['flume']['http'])



if config.has_key('namenode') and config['namenode'].has_key('url'):
    print 'run hadoop namenode metrics'
    hadoopJMXDataProcessor = HadoopJMXDataProcessor()
    hadoopJMXDataProcessor.process(config['namenode']['url'])