#!/usr/bin/python
from services.AppService import AppService
from datetime import datetime, timedelta
import random
import sys
import inspect
import os
app = 'topface'

thisPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory

appService = AppService(thisPath + '/../app_configs')

config = appService.getAppConfig(app)

keys = config['keys']
tags = config['tags']
tagSettings = config['tagSettings']
bunches = config['bunches']

def tag_to_string(tags):
    x = []
    for k, v in tags.items():
        x.append('%(k)s=%(v)s'%{'k':k, 'v':v})
    return ';'.join(x)

def getTagValue(tag):
    tagSetting = tagSettings[tag]
    if tagSetting['type'] == 'choose':
        values = tagSetting['values']

        if isinstance(values, list):
            return random.choice(values)
        else:
            return random.choice(values.keys())
    elif tagSetting['type'] == 'boolean':
        return random.choice([0, 1])
    elif tagSetting['type'] == 'int':
        min = 0
        max = 99
        if tagSetting.has_key('min'):
            min = tagSetting['min']
        if tagSetting.has_key('max'):
            max = tagSetting['max']
        return random.randint(min, max)
    else:
        return random.choice(['string1', 'string2', 'string3'])

et = datetime.now()


for __day in range(0, 100):
    et = et - timedelta(days = 1)
    date = et.date()
    time = et.time()
    et = et - timedelta(hours = time.hour, minutes = time.minute, seconds = time.second)

    logs = []

    for i in range(300):
        params = {}
        key = random.choice(keys.keys())
        for tag in keys[key]['mustHaveTags']:
            params[tag] = getTagValue(tag)

        for bunch in keys[key]['autoLoadBunches']:
            for tag in bunches[bunch]['tags']:
                params[tag] = getTagValue(tag)

        dt = et + timedelta(hours = random.randint(0, 23), minutes = random.randint(0, 59), seconds = random.randint(0, 59))
        date = dt.date()
        time = dt.time()
        userId = 0
        logstring = ','.join([tag_to_string(params), str(userId),dt.strftime('%Y-%m-%d %H:%M:%S'), str(time.hour), str(time.minute), str(time.second), str(date.year), str(date.month), str(date.day)])

        print logstring
        logs.append(logstring)

    folder = thisPath + '/testData/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/'
    if not os.path.exists(folder):
        os.makedirs(folder)
    f = open(folder + 'data.txt', 'w')
    f.write("\n".join(logs))
    f.close()