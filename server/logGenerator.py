from service import AppService
from datetime import datetime, timedelta
import random
app = 'topface'

config = AppService.getAppKeyConfig(app)

keys = config['keys']
tags = config['tags']

def tag_to_string(tags):
    x = []
    for k, v in tags.items():
        x.append('%(k)s=%(v)s'%{'k':k, 'v':v})
    return ';'.join(x)

et = datetime.now()
et = et + timedelta(days = 1)
date = et.date()
time = et.time()
et = et - timedelta(hours = time.hour, minutes = time.minute, seconds = time.second)

for i in range(100):

    params = {}
    key = random.choice(keys.keys())
    for tag in keys[key]['mustHaveTags']:
        if tags[tag]['type'] == 'choose':
            params[tag] = random.choice(tags[tag]['variants'])
        else:
            params[tag] = random.choice(['string1', 'string2', 'string3'])
    dt = et + timedelta(hours = random.randint(0, 23), minutes = random.randint(0, 59), seconds = random.randint(0, 59))
    date = dt.date()
    time = dt.time()
    logstring = ','.join([tag_to_string(params), dt.strftime('%Y-%m-%d %H:%M:%S'), str(time.hour), str(time.minute), str(time.second), str(date.year), str(date.month), str(date.day)])
    print logstring


