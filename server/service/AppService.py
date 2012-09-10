# -*- coding: utf-8 -*-
import json, os, re

class AppService():
    nameR = re.compile('^(.*)\.json$')

    def __init__(self, config_folder):
        self.folder = config_folder

    def getAppConfigList(self):
        '''
        return list of available config apps
        stored in app_config_path
        '''
        return [self.nameR.search(file).group(1) for file in os.listdir(self.folder)]

    def getAppConfig(self, appCode):
        '''
        return app config dict
        '''
        return json.load(open(self.folder + '/' + appCode + '.json', 'r'))

    def getConfigTags(self, appName, keyName, prefix):
        config = self.getAppConfig(appName)
        keyConf = config['keys'][keyName]

        raw_json = {}
        if keyConf.has_key(prefix + 'HaveTags'):
            for tag in keyConf[prefix + 'HaveTags']:
                raw_json[tag] = config['tags'][tag]


        if keyConf.has_key(prefix + 'HaveBunches'):
            for slice in keyConf[prefix + 'HaveBunches']:
                for tag in config['bunches'][slice]:
                    raw_json[prefix + 'HaveTags'][tag] = config['tags'][tag]

        return raw_json

    def getConfigTags(self, appName, keyName, prefix):
        config = self.getAppConfig(appName)
        keyConf = config['keys'][keyName]

        raw_json = {}
        if keyConf.has_key(prefix + 'Tags'):
            for tag in keyConf[prefix + 'Tags']:
                raw_json[tag] = config['tags'][tag]

        # load bunch
        if keyConf.has_key(prefix + 'Bunches'):
            for bunchName in keyConf[prefix + 'Bunches']:
                for tag in config['bunches'][bunchName]['tags']:
                    raw_json[tag] = config['tags'][tag]

        return raw_json


    def getKeys(self, appName):
        config = self.getAppConfig(appName)
        return config['keys']

    def saveConfig(self, data):
        if u'appname' in data.keys():
            appName = data[u'appname']
            f = open(self.folder + '/' + appName + '.json', 'w+')
            f.write(json.dumps(data))
            f.close()
        else:
            raise Error('Cant find appname in config')


class AppNameService(object):

    def __init__(self, appConfig, task):
        self.appConfig = appConfig
        self.task = task

    def getKeyNameByIndex(self, index):
        '''
        return key name by taskItem index
        '''
        taskItem = self.task.getTaskItem(index)
        if taskItem:
            key = taskItem.key
            if self.appConfig['keys'].has_key(key) and self.appConfig['keys'][key].has_key('name'):
                return self.appConfig['keys'][key]['name']
        return 'not name for index ' + str(index)

    def getParamNameValue(self, tagName, value):
        '''

        '''
        tag_name = tagName
        tag_value = value

        if self.appConfig['tags'].has_key(tagName):
            tagConf = self.appConfig['tags'][tagName]
            if tagConf.has_key('name'):
                tag_name = tagConf['name']

            type = None
            if tagConf.has_key('type'):
                type = tagConf['type']

            extra = []
            if tagConf.has_key('extra'):
                extra = tagConf['extra']

            if type == 'choose':
                if 'keyValues' in extra and tagConf['values'].has_key(value):
                    tag_value = tagConf['values'][value]

            elif type == 'boolean':
                if bool(value):
                    tag_value = u'Да'
                else:
                    tag_value = u'Нет'

        return u'{0} = {1}'.format(tag_name, tag_value)

    def getSeriaName(self):
        return 'seria name'




