#!/usr/bin/python

import ConfigParser
import os
from utils.state import State

confPath = os.path.abspath('server.cnf')

configParser = ConfigParser.RawConfigParser()
configParser.read(['server.cnf'])

config = {}
sections = configParser.sections()
for section in sections:
    items = configParser.items(section)
    config[section] = {}
    for k, v in items:
        config[section][k] = v


dirList=os.listdir('sql')
files = []
for fname in dirList:
    index, name = fname.split('-', 1)
    files.append((int(index), name))

# sort by index
files = sorted(files)

state = State()
state.set('currentDBVersion', 0)
currentDBVersion = state.get('currentDBVersion')
print currentDBVersion
for index, name in files:
    if index > currentDBVersion:
        # run script
        command = 'mysql -u{0} -p{1} {2} < {3}'.format(config['mysql']['user'], config['mysql']['password'], config['mysql']['dbname'], 'sql/' + str(index) + '-' + name)
        print 'run: ' + command
        os.system(command)

        currentDBVersion = index
        state.set('currentDBVersion', currentDBVersion)






