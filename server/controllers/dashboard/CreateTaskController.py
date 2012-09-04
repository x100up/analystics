# -*- coding: utf-8 -*-
from controllers.BaseController import BaseController
from service.QueryService import HiveQueryConstructor
from worker import HiveWorker
from models.Worker import Worker
from models.Task import Task, TaskItem
import uuid, tornado.web
from datetime import datetime, timedelta
from service.WorkerService import WorkerService
from sqlalchemy import desc, func
from service.AppService import AppService

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
            worker = dbSession.query(Worker).filter_by(uuid = baseTask).first()
            workerService = WorkerService(self.getConfig('core', 'result_path'), worker)
            task = workerService.getTask()
        else:
            taksItem = TaskItem(delta = timedelta(days = -1), index = 1)
            task = Task(appname = app.code)
            task.addTaskItem(taksItem)

        keys = set()
        for taskItem in task.items:
            if taskItem.key:
                keys.add(taskItem.key)

        key_configs = {}
        if len(keys):
            appService = AppService(self.getConfig('core', 'app_config_path'))
            for key in keys:
                key_configs[key] = {
                    "mustHaveTags": appService.getConfigTags(app.code, key, 'must'),
                    "canHaveTags": appService.getConfigTags(app.code, key, 'can'),
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

            task.addTaskItem(taskItem)


        constructor = HiveQueryConstructor(task)
        query = constructor.getHiveQuery()

        user = self.get_current_user()

        # объект для записи в базу
        worker = Worker()
        worker.uuid = str(uuid.uuid4())
        worker.userId = user.userId
        worker.startDate = datetime.now()
        worker.status = Worker.STATUS_ALIVE
        worker.appId = app.appId
        session = self.getDBSession()
        session.add(worker)
        session.commit()

        # создаем WorkerService - он будет связывать тред с файловой системой
        workerService = WorkerService(self.getConfig('core', 'result_path'), worker)
        workerService.setQuery(query)
        workerService.setFields(constructor.getFields())
        workerService.setTask(task)
        workerService.init()

        # тут будем констуровать запрос
        workerThread = HiveWorker.HiveWorker(workerService)

        # передает sessionmaker т.к. он создает сеессию в пределах треда
        workerThread.mysqlSessionMaker = self.getSessionMaker()
        workerThread.folderForWorkerService = self.getConfig('core', 'result_path')
        workerThread.host = self.getConfig('hive', 'host')
        workerThread.port = int(self.getConfig('hive', 'port'))
        workerThread.setName(worker.uuid)
        workerThread.start()

        self.write(str(query))

        #self.redirect("/dashboard?newJob=" + str(worker.uuid))