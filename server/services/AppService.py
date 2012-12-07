# -*- coding: utf-8 -*-
import json, os, re
from components.AnalyticsException import AnalyticsException
from models.AppConfig import AppConfig

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
                self.appConfCache[appCode] = AppConfig(json.load(f))
            except ValueError as valueError:
                raise AnalyticsException(u'Ошибка при чтении конфигурации приложения {}'.format(self.folder + '/' + appCode + '.json'), valueError)
        return self.appConfCache[appCode]

    def getNewAppConfig(self, appCode):
        return self.getAppConfig(appCode)


    def isConfigExist(self, appCode):
        return os.path.exists(self._getFilePath(appCode))

    def createEmptyConfig(self, appCode):
        config = AppConfig()
        self.appConfCache[appCode] = config
        self.newSaveConfig(AppConfig())
        pass

    def _getFilePath(self, appCode):
        return self.folder + '/' + appCode + '.json'


    def saveSettings(self, appName, tags = None, keys = None, bunches = None):
        config = self.getAppConfig(appName)
        if tags:
            config['tags'] = tags
        if keys:
            config['keys'] = keys
        if bunches:
            config['bunches'] = bunches
        self.saveConfig(config)


    def saveConfig(self, data):
        if u'appname' in data.keys():
            appName = data[u'appname']
            f = open(self.folder + '/' + appName + '.json', 'w+')
            f.write(json.dumps(data, sort_keys=True, indent=4))
            f.close()
        else:
            raise Error('Cant find appname in config')

    def newSaveConfig(self, appConfig):
        self.saveConfig(appConfig.dumpToJSON())

    def getKnowAppList(self):
        return [ file.replace('.json', '') for file in os.listdir(self.folder)]
