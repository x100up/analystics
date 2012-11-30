# -*- coding: utf-8 -*-
import json, os, re
from components.AnalyticsException import AnalyticsException

class AppService():


    KEYS_JSON_INDEX = 'keys'
    BUNCHES_JSON_INDEX = 'bunches'
    TAGS_JSON_INDEX = 'tags'

    nameR = re.compile('^(.*)\.json$')

    def __init__(self, config_folder):
        self.folder = config_folder
        self.appConfCache = {}

    def getAppConfigList(self):
        '''
        return list of available config apps
        stored in app_config_path
        '''
        list = []
        for file in os.listdir(self.folder):
            match = self.nameR.search(file)
            if match:
                list.append(match.group(1))
        return list

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
            'keys' : {},
            'tags':{}
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
        if config.has_key('tags'):
            return config['tags'].keys()
        return []

    def getTagSettings(self, appName):
        '''
            return list of tags
        '''
        config = self.getAppConfig(appName)
        if config.has_key(u'tags'):
            return config[u'tags']
        return []

    def saveSettings(self, appName, tags = None, keys = None, bunches = None):
        config = self.getAppConfig(appName)
        if tags:
            config['tags'] = tags
        if keys:
            config['keys'] = keys
        if bunches:
            config['bunches'] = bunches
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

    def getBunches(self, appName):
        config = self.getAppConfig(appName)
        if config.has_key(self.BUNCHES_JSON_INDEX):
            return config[self.BUNCHES_JSON_INDEX]
        return {}

    def saveConfig(self, data):
        if u'appname' in data.keys():
            appName = data[u'appname']
            f = open(self.folder + '/' + appName + '.json', 'w+')
            f.write(json.dumps(data, sort_keys=True, indent=4))
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

