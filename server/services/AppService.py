# -*- coding: utf-8 -*-
import json, os, re

class AppService():
    nameR = re.compile('^(.*)\.json$')

    def __init__(self, config_folder):
        self.folder = config_folder
        self.appConfCache = {}

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
        if not self.appConfCache.has_key(appCode):
            self.appConfCache[appCode] = json.load(open(self.folder + '/' + appCode + '.json', 'r'))
        return self.appConfCache[appCode]

    def getTagList(self, appName):
        '''
            return list of tags
        '''
        config = self.getAppConfig(appName)
        if config.has_key('tags'):
            return config['tags']
        return []

    def getTagSettings(self, appName):
        '''
            return list of tags
        '''
        config = self.getAppConfig(appName)
        if config.has_key('tagSettings'):
            return config['tagSettings']
        return []

    def saveTagSettings(self, appName, settings):
        config = self.getAppConfig(appName)
        config['tagSettings'] = settings
        self.saveConfig(config)

    def getAppTags(self, appName, keyName, prefix):
        config = self.getAppConfig(appName)
        keyConf = config['keys'][keyName]

        raw_json = {}
        if keyConf.has_key(prefix + 'Tags'):
            for tag in keyConf[prefix + 'Tags']:
                raw_json[tag] = None

        # load bunch
        if keyConf.has_key(prefix + 'Bunches'):
            for bunchName in keyConf[prefix + 'Bunches']:
                for tag in config['bunches'][bunchName]['tags']:
                    raw_json[tag] = None

        settings = self.getTagSettings(appName)
        for tag_name in raw_json.keys():
            if settings.has_key(tag_name):
                raw_json[tag_name] = settings[tag_name]

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


    def getKnowAppList(self):
        return [ file.replace('.json', '') for file in os.listdir(self.folder)]

