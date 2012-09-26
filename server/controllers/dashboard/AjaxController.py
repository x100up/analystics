# -*- coding: utf-8 -*-
from controllers.BaseController import AjaxController
from services.AppService import AppService
from models.Task import TaskItem
from models.Worker import Worker
from models.App import App
from services import ThredService
from components.TaskFactory import createTaskFromRequestArguments
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

        taskItem = TaskItem(index = index, key = keyName)

        appService = AppService(self.application.getAppConfigPath())
        tags = {
            "tags": dict(appService.getAppTags(appName, keyName, 'mustHave').items() +
             appService.getAppTags(appName, keyName, 'canHave').items() +
             appService.getAppTags(appName, keyName, 'autoLoad').items())
        }

        self.render('blocks/tag_container.jinja2', {'tags':tags, 'taskItem': taskItem, 'values':{}})

class GetKeyForm(AjaxController):
    def post(self, *args, **kwargs):
        appCode = self.get_argument('appCode')
        index = self.get_argument('index')
        taskItem = TaskItem(index = index)
        self.render('blocks/key_container.jinja2', {'taskItem':taskItem})

class GetKeys(AjaxController):

    def get(self, appCode):
        keyIndex = self.get_argument('index')
        self.checkAppAccess(appCode)
        appService = AppService(self.application.getAppConfigPath())
        keys = appService.getKeys(appCode)

        app = self.getDBSession().query(App).filter(App.code == appCode).first()

        self.render('blocks/key_select.jinja2', {'_keys':keys, 'index':keyIndex, 'appName':app.name})


class GatTasksProgress(AjaxController):
    def post(self, *args, **kwargs):
        arguments = []
        appIdToWorkerId = {}
        blank = u'None'

        for workerId, stageCount in self.request.arguments.items():
            arguments.append( (int(workerId), stageCount) )

        #resourceManagerService = ResourceManagerService(self.getConfigValue(Config.HADOOP_YARN_RESOURCEMANAGER))

        # получаем прогресс задач
        #progressResult = None
        #diedWorkers = []
        #
        #if toGetProgress:
        #    progressResult = resourceManagerService.getWorkerProgresses(toGetProgress)

        #print progressResult

        diedWorkers = []
        workerIds = [workerId for workerId, stageCount in arguments]
        aliveThreadNames = ThredService.getAliveThreads()
        for workerId in workerIds:
            if not 'worker-' + str(workerId) in aliveThreadNames:
                diedWorkers.append(workerId)

        workerStates = []
        if diedWorkers:
            db = self.getDBSession()
            workerStates = db.query(Worker.workerId, Worker.status).filter(Worker.workerId.in_(diedWorkers)).all()
        print workerStates
        self.renderJSON({'workerStates':workerStates})


class CopyTaskKey(AjaxController):
    '''
    remote copy task key
    '''
    def post(self, *args, **kwargs):
        copy_index = self.get_argument('copy_key_index')
        new_index = self.get_argument('new_index')
        appname = self.get_argument('appname')
        task = createTaskFromRequestArguments(self.request.arguments)
        taskItem = task.getTaskItem(copy_index)
        taskItem.index = new_index
        appService = AppService(self.application.getAppConfigPath())
        key_configs = appService.getKeyConfigs(appname, [taskItem.key])
        self.render('blocks/key_container.jinja2', {'taskItem': taskItem, 'key_configs':key_configs})

