# -*- coding: utf-8 -*-
from components import HiveWorker
from components.HiveQueryConstructor import  HiveQueryConstructor
from controllers.BaseController import BaseController
from models.Worker import Worker
from models.Task import Task, TaskItem
from datetime import datetime, timedelta
from services.WorkerService import WorkerService
from services.AppService import AppService
from components.TaskFactory import createTaskFromRequestArguments
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
            # задача основана на другой задаче
            worker = dbSession.query(Worker).filter_by(workerId = baseTask).first()
            workerService = WorkerService(self.application.getResultPath(), worker)
            task = workerService.getTask()
            keys_loaded = len(task.items)
        else:
            taskItem = TaskItem(index = 1)
            task = Task(appname = app.code)
            task.addTaskItem(taskItem)
            keys_loaded = 0

        keys = set()
        for index, taskItem in task.items.items():
            if taskItem.key:
                keys.add(taskItem.key)

        key_configs = {}
        if len(keys):
            appService = AppService(self.application.getAppConfigPath())
            key_configs = appService.getKeyConfigs(app.code, keys)


        self.render('dashboard/new.jinja2', {'task':task, 'app':app, 'key_configs':key_configs, 'js_vars': {'keys_loaded':keys_loaded}})

    def post(self, *args, **kwargs):
        app = self.checkAppAccess(args)

        # создаем задачу из аргументов
        task = createTaskFromRequestArguments(self.request.arguments)

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

        # конструирем запрос
        constructor = HiveQueryConstructor(task)
        query = constructor.getHiveQuery(worker.workerId)
        task.stageCount = constructor.getStageCount()

        # создаем WorkerService - он будет связывать тред с файловой системой
        workerService = WorkerService(self.application.getResultPath(), worker)
        workerService.setQuery(query)
        workerService.setFields(constructor.getFields())
        workerService.setTask(task)
        workerService.init()

        # тут будем констуровать запрос
        workerThread = HiveWorker.HiveWorker(workerService)

        # передает sessionmaker т.к. он создает сеессию в пределах треда
        workerThread.mysqlSessionMaker = self.application.getSessionMaker()
        workerThread.folderForWorkerService = self.application.getResultPath()
        workerThread.host = self.getConfigValue('hive_host')
        workerThread.port = int(self.getConfigValue('hive_port'))
        workerThread.setName('worker-' + str(worker.workerId))
        workerThread.setTask(task)
        workerThread.start()

        self.redirect('/dashboard/app/' + app.code + '/')