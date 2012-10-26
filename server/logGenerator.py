#!/usr/bin/python
from services.AppService import AppService
from datetime import datetime, timedelta
import random
from optparse import OptionParser
import inspect
import os

rootPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory

optParser = OptionParser()
optParser.add_option("-a", "--app", dest="appname", help="application name")
optParser.add_option("-k", "--key", dest="key", help="key code")
optParser.add_option("-c", "--count", dest="rows count", help="count of log rows to generate")

(options, args) = optParser.parse_args()
options = options.__dict__

appService = AppService(rootPath + '/../app_configs/')


if options['appname'] is None:
    availale_apps = appService.getAppConfigList()
    print 'App name is not set'
    print 'Availale app names: ' + str(availale_apps)
    exit()

if options['key'] is None:
    availale_apps = appService.getAppConfigList()
    print 'key code is not set'
    exit()

key = options['key']
app = options['appname']

print 'Generate for ' + app

config = appService.getAppConfig(app)

keys = config['keys']
tags = config['tags']
tagSettings = config['tagSettings']
if config.has_key('bunches'):
    bunches = config['bunches']
else:
    bunches = []

_string_vals = {
    '_default':['string1', 'string2', 'string3']
    'cnt': [],
    'ad':['advmaker', 'energyGift2B', 'energyGiftB', 'newmain', 'oldmain'],
    'app':[],
    'cit':[]
}

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
        if _string_vals.has_key(tag):
            return random.choice(_string_vals[tag])
        else:
            return random.choice(_string_vals['_default'])

et = datetime.now()


for __day in range(0, 500):
    et = et - timedelta(days = 1)
    date = et.date()
    time = et.time()
    et = et - timedelta(hours = time.hour, minutes = time.minute, seconds = time.second)

    logs = []
    count = random.randint(200, 400)
    print count
    for i in range(count):
        params = {}
        for tag in keys[key]['mustHaveTags']:
            params[tag] = getTagValue(tag)

        if keys[key].has_key('autoLoadBunches'):
            for bunch in keys[key]['autoLoadBunches']:
                for tag in bunches[bunch]['tags']:
                    params[tag] = getTagValue(tag)

        dt = et + timedelta(hours = random.randint(0, 23), minutes = random.randint(0, 59), seconds = random.randint(0, 59))
        date = dt.date()
        time = dt.time()
        userId = 0
        logstring = ','.join([tag_to_string(params), str(userId),dt.strftime('%Y-%m-%d %H:%M:%S'), str(time.hour), str(time.minute), str(time.second), str(date.year), str(date.month), str(date.day)])

        logs.append(logstring)

    folder = rootPath + '/testData/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/'
    print folder
    if not os.path.exists(folder):
        os.makedirs(folder)
    f = open(folder + 'data.txt', 'w')
    f.write("\n".join(logs))
    f.close()