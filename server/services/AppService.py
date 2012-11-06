# -*- coding: utf-8 -*-
import json, os, re
from pprint import pprint
from components.AnalyticsException import AnalyticsException

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
            try:
                f = open(self._getFilePath(appCode), 'r')
                self.appConfCache[appCode] = json.load(f)
            except ValueError as valueError:
                raise AnalyticsException(u'Ошибка при чтении конфигурации приложения {}'.format(self.folder + '/' + appCode + '.json'), valueError)
        return self.appConfCache[appCode]

    def isConfigExist(self, appCode):
        return os.path.exists(self._getFilePath(appCode))

    def createEmptyConfig(self, appCode):
        config = {
            'appname': appCode,
            'keys' : {}
        }
        self.appConfCache[appCode] = config
        self.saveConfig(config)
        pass

    def _getFilePath(self, appCode):
        return self.folder + '/' + appCode + '.json'

    def getTagList(self, appName):
        '''
            return list of tags
        '''
        config = self.getAppConfig(appName)
        if config.has_key('tagSettings'):
            return config['tagSettings'].keys()
        return []

    def getTagSettings(self, appName):
        '''
            return list of tags
        '''
        config = self.getAppConfig(appName)
        if config.has_key(u'tagSettings'):
            return config[u'tagSettings']
        return []

    def saveSettings(self, appName, tagSettings = None, keyConfig = None):
        config = self.getAppConfig(appName)
        config['tagSettings'] = tagSettings
        if keyConfig:
            config['keys'] = keyConfig
        self.saveConfig(config)

    def getAppTags(self, appName, keyName):
        '''

        '''
        config = self.getAppConfig(appName)
        keyConf = config['keys'][keyName]

        raw_json = {}
        if keyConf.has_key('tags'):
            raw_json = keyConf['tags']

        # load bunch
        if keyConf.has_key('bunches'):
            for bunchName in keyConf['bunches']:
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


    def getKeyConfigs(self, app_code, keys):
        key_configs = {}
        for key in keys:
            key_configs[key] = {
                "tags": self.getAppTags(app_code, key)
                }
        return key_configs

