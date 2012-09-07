from service.AppService import AppService
from datetime import datetime, timedelta
import random, sys
app = 'topface'

appService = AppService('app_configs')

config = appService.getAppConfig(app)

keys = config['keys']
tags = config['tags']
bunches = config['bunches']

def tag_to_string(tags):
    x = []
    for k, v in tags.items():
        x.append('%(k)s=%(v)s'%{'k':k, 'v':v})
    return ';'.join(x)

def getTagValue(tag):
    tc = tags[tag]
    if tc['type'] == 'choose':
        values = tc['values']

        if isinstance(values, list):
            return random.choice(values)
        else:
            return random.choice(values.keys())
    elif tc['type'] == 'boolean':
        return random.choice([0, 1])
    elif tc['type'] == 'int':
        min = 0
        max = sys.maxint
        if tc.has_key('min'):
            min = tc['min']
        if tc.has_key('max'):
            max = tc['max']
        return random.randint(min, max)
    else:
        return random.choice(['string1', 'string2', 'string3'])

et = datetime.now()
et = et - timedelta(days = 1)
date = et.date()
time = et.time()
et = et - timedelta(hours = time.hour, minutes = time.minute, seconds = time.second)

for i in range(100):

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
    logstring = ','.join([tag_to_string(params), dt.strftime('%Y-%m-%d %H:%M:%S'), str(time.hour), str(time.minute), str(time.second), str(date.year), str(date.month), str(date.day)])
    print logstring


