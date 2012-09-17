# -*- coding: utf-8 -*-
from controllers.BaseController import BaseController
from service.QueryService import HiveQueryConstructor
from worker import HiveWorker
from models.Worker import Worker
from models.Task import Task, TaskItem
from datetime import datetime, timedelta
from service.WorkerService import WorkerService
from service.AppService import AppService
import tornado.web

class CreateAction(BaseController):
    """
        Добавление новой задачи
    """
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        app = self.checkAppAccess(args)
        dbSession = self.getDBSession()
        baseTask = self.get_argument('baseOn', False)
        if baseTask:
            worker = dbSession.query(Worker).filter_by(workerId = baseTask).first()
            workerService = WorkerService(self.application.getResultPath(), worker)
            task = workerService.getTask()
        else:
            now = datetime.now()
            time = now.time()
            start = now - timedelta(hours = time.hour, minutes = time.minute, seconds = time.second)
            end = start + timedelta(days = 1)
            taksItem = TaskItem(start = start, end = end, index = 1)
            task = Task(appname = app.code)
            task.addTaskItem(taksItem)

        keys = set()
        for index, taskItem in task.items.items():
            if taskItem.key:
                keys.add(taskItem.key)

        key_configs = {}
        if len(keys):
            appService = AppService(self.application.getAppConfigPath())
            for key in keys:
                key_configs[key] = {
                    "mustHaveTags": appService.getAppTags(app.code, key, 'mustHave'),
                    "canHaveTags": appService.getAppTags(app.code, key, 'canHave'),
                }

        self.render('dashboard/new.jinja2', {'task':task, 'app':app, 'key_configs':key_configs})

    def post(self, *args, **kwargs):
        app = self.checkAppAccess(args)
        group_interval = self.get_argument('group_interval', False)
        # создаем задачу
        task = Task(appname = app.code, interval = group_interval)
        indexes = self.get_arguments('indexes')
        for index in indexes:
            key = self.get_argument('key_' + index, False)
            if not key:
                continue

            start = self.get_argument('start_'+ index, False)
            start = datetime.strptime(start, "%m/%d/%Y %H:%M")
            end = self.get_argument('end_'+ index, False)
            end = datetime.strptime(end, "%m/%d/%Y %H:%M")

            taskItem = TaskItem(key = key, start = start, end = end, index = index)
            # разбираем тег для ключа
            tagNames = self.get_arguments('tag_' + index + '_name', [])

            for tagName in tagNames:
                values = self.get_arguments('tag_' + index + '_' + tagName, None)
                if not values is None:
                    taskItem.addCondition(tagName, values)

                group = self.get_argument('group_' + index + '_' + tagName, None)
                if not group is None:
                    taskItem.addTagGroup(tagName)

            task.addTaskItem(taskItem)


        constructor = HiveQueryConstructor(task)
        query = constructor.getHiveQuery()

        user = self.get_current_user()

        # объект для записи в базу
        worker = Worker()
        worker.userId = user.userId
        worker.startDate = datetime.now()
        worker.status = Worker.STATUS_ALIVE
        worker.appId = app.appId
        session = self.getDBSession()
        session.add(worker)
        session.commit()

        # создаем WorkerService - он будет связывать тред с файловой системой
        workerService = WorkerService(self.application.getResultPath(), worker)
        workerService.setQuery(query)
        workerService.setFields(constructor.getFields())
        workerService.setTask(task)
        workerService.init()

        # тут будем констуровать запрос
        workerThread = HiveWorker.HiveWorker(workerService)

        # передает sessionmaker т.к. он создает сеессию в пределах треда
        workerThread.mysqlSessionMaker = self.getSessionMaker()
        workerThread.folderForWorkerService = self.application.getResultPath()
        workerThread.host = self.getConfigValue('hive_host')
        workerThread.port = int(self.getConfigValue('hive_port'))
        workerThread.setName('worker-' + str(worker.workerId))
        workerThread.setTask(task)
        workerThread.start()

        self.redirect('/dashboard/app/' + app.code + '/')