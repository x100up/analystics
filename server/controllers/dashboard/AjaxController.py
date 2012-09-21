# -*- coding: utf-8 -*-
from controllers.BaseController import AjaxController
from services.AppService import AppService
from models.Task import TaskItem
from datetime import timedelta
from models.Config import Config
from services.ResourceManagerService import ResourceManagerService
from services import ThredService
from models.Worker import Worker
import re

class KeyAutocompleteAction(AjaxController):

    def get(self, *args, **kwargs):
        appName = self.get_argument('app', None)
        query = self.get_argument('query', None)
        if appName is None:
            self.send_ajax_error('Неверный запрос')

        appService = AppService(self.application.getAppConfigPath())
        config = appService.getAppConfig(appName)
        keysList = config['keys'].keys()

        regexp = re.compile('^' + query + '.*')
        list = filter(lambda x:regexp.match(x) , keysList)

        self.renderJSON({'query' : query, 'suggestions' : list})


class KeyConfigurationAction(AjaxController):

    def post(self, *args, **kwargs):
        keyName = self.get_argument('key', None)
        appName = self.get_argument('app', None)
        index = self.get_argument('index', 1)

        appService = AppService(self.application.getAppConfigPath())
        tags = {
            "tags": dict(appService.getAppTags(appName, keyName, 'mustHave').items() +
             appService.getAppTags(appName, keyName, 'canHave').items() +
             appService.getAppTags(appName, keyName, 'autoLoad').items())
        }

        self.render('blocks/tag_container.jinja2', {'tags':tags, 'key': keyName, 'index': index, 'values':{}})

class GetKeyForm(AjaxController):
    def post(self, *args, **kwargs):
        keyIndex = self.get_argument('index')
        taskItem = TaskItem(delta = timedelta(days = -1))
        taskItem.index = keyIndex
        self.render('blocks/key_container.jinja2', {'taskItem':taskItem})

class GetKeys(AjaxController):
    def get(self, appName):
        keyIndex = self.get_argument('index')
        self.checkAppAccess(appName)
        appService = AppService(self.application.getAppConfigPath())
        keys = appService.getKeys(appName)
        self.render('blocks/key_select.jinja2', {'_keys':keys, 'index':keyIndex})


class GatTasksProgress(AjaxController):
    def post(self, *args, **kwargs):
        arguments = []
        appIdToWorkerId = {}
        blank = u'None'

        for workerid, appid in self.request.arguments.items():
            arguments.append( (appid[0], int(workerid)) )


        toFindAppId = []
        toGetProgress = []
        for appId, workerId in arguments:
            if appId == blank:
                toFindAppId.append(workerId)
            else:
                toGetProgress.append(appId)
                appIdToWorkerId[appId] = workerId

        # находим дентификаторы приложений
        hyrmurl = self.getConfigValue(Config.HADOOP_YARN_RESOURCEMANAGER)
        resourceManagerService = ResourceManagerService(hyrmurl)

        appIdResult = None
        if toFindAppId and hyrmurl:
            appIdResult = resourceManagerService.getAppIdsForWrokers(toFindAppId)
            for workerId, appId in appIdResult:
                toFindAppId.remove(workerId)
                toGetProgress.append(appId)
                appIdToWorkerId[appId] = workerId

        needCheckThread = toFindAppId # нужно проверить жив ли тред

        # получаем прогресс задач
        progressResult = None
        diedWorkers = []
        if toGetProgress:
            progressResult = resourceManagerService.getAppProgresses(toGetProgress)

        if  (not progressResult) or  (len(progressResult) != len(toGetProgress)):
            print needCheckThread
            # если количество прогрессов не совпадает
            # то мы проверяем жив ли тред
            if progressResult:
                for appId, progress in progressResult:
                    if not appId in toGetProgress:
                        needCheckThread.append(appIdToWorkerId[appId])
            if needCheckThread:
                aliveThreadNames = ThredService.getAliveThreads()

                for workerId in needCheckThread:
                    if not 'worker-' + str(workerId) in aliveThreadNames:
                        diedWorkers.append(workerId)


        print {'appIdResult' : appIdResult, 'progressResult' : progressResult, 'diedWorkers': diedWorkers}
        self.renderJSON({'appIdResult' : appIdResult, 'progressResult' : progressResult, 'diedWorkers': diedWorkers})