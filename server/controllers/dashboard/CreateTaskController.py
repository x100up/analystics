# -*- coding: utf-8 -*-
from components import HiveWorker
from components.HiveQueryConstructor import  HiveQueryConstructor
from controllers.BaseController import BaseController, AjaxController
from models.Worker import Worker
from models.Task import Task, TaskItem
from datetime import datetime
from services.WorkerService import WorkerService
from services.AppService import AppService
from components.TaskFactory import createTaskFromRequestArguments
from components.NameConstructor import NameConstructor
from models.TaskTemplate import TaskTemplate, TaskTemplateFile
from sqlalchemy.sql import or_, and_
import tornado.web
from services import ThredService


class CreateTaskController():

    def createHiveWorker(self, workerService):
        workerThread = HiveWorker.HiveWorker(workerService)
        # передает sessionmaker т.к. он создает сеессию в пределах треда
        workerThread.mysqlSessionMaker = self.application.scoped_session
        workerThread.folderForWorkerService = self.application.getResultPath()
        workerThread.host = self.getConfigValue('hive_host')
        workerThread.port = int(self.getConfigValue('hive_port'))
        workerThread.setName('worker-' + str(workerService.getWorker().workerId))
        workerThread.setVersion(workerService.version)
        workerThread.setTask(workerService.getTask())
        return workerThread


class CreateAction(CreateTaskController, AjaxController):
    """
        Добавление новой задачи
    """
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        app = self.checkAppAccess(args)
        dbSession = self.getDBSession()
        baseTask = self.get_argument('baseOn', False)
        template = self.get_argument('template', False)
        if baseTask:
            # задача основана на другой задаче
            worker = dbSession.query(Worker).filter_by(workerId = baseTask).first()
            workerService = WorkerService(self.application.getResultPath(), worker)
            task = workerService.getTask()
        elif template:
            templateId = int(template)
            userId = self.get_current_user().userId
            taskTemplate = dbSession.query(TaskTemplate).filter(
                    and_(TaskTemplate.taskTemplateId == templateId,
                    or_(    TaskTemplate.userId == userId,
                            TaskTemplate.shared == TaskTemplate.SHARED_YES))
                    ).first()

            if taskTemplate:
                taskTemplateFile = TaskTemplateFile.read(self.application.getTemplatePath(), taskTemplate)
                task = taskTemplateFile.getTask()
            else:
                self.showFatalError(u'Ошибка при доступе к шаблону')
                return

        else:
            taskItem = TaskItem(index = 1)
            task = Task(appname = app.code)
            task.addTaskItem(taskItem)

        keys_loaded = len(task.items)

        keys = set()
        for index, taskItem in task.items.items():
            if taskItem.key:
                keys.add(taskItem.key)

        key_configs = {}
        if len(keys):
            appService = AppService(self.application.getAppConfigPath())
            key_configs = appService.getKeyConfigs(app.code, keys)

        html = self.render('dashboard/new.jinja2', {'task':task, 'app':app, 'key_configs':key_configs}, _return = True)

        self.renderJSON({'html': html, 'vars':{'keys_loaded':keys_loaded}})

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

        # генерируем имя запроса
        appService = AppService(self.application.getAppConfigPath())
        appConfig = appService.getAppConfig(app.code)
        nameConstructor = NameConstructor(appConfig, task)
        worker.name = nameConstructor.generateTaskName()

        session = self.getDBSession()
        session.add(worker)
        session.commit()

        # конструирем запрос
        constructor = HiveQueryConstructor(task, appConfig)
        query = constructor.getHiveQuery(worker.workerId)


        task.stageCount = constructor.getStageCount()
        # создаем WorkerService - он будет связывать тред с файловой системой
        workerService = WorkerService(self.application.getResultPath(), worker)
        workerService.setQuery(query)
        workerService.setTask(task)
        workerService.init()

        # создаем и запускаем тред
        workerThread = self.createHiveWorker(workerService)
        workerThread.start()

        self.redirect('/dashboard/app/' + app.code + '/#new_task/' + str(worker.workerId))

class RecalculateAction(CreateTaskController, BaseController):

    def get(self, *args, **kwargs):
        app = self.checkAppAccess(args)
        workerId = self.get_argument('workerId')
        workerId = int(workerId)
        dbSession = self.getDBSession()

        # загружаем воркер из базы
        worker = dbSession.query(Worker).filter_by(workerId = workerId).first()
        worker.status = Worker.STATUS_ALIVE
        worker.startDate = datetime.now()
        worker.endDate = None
        dbSession.add(worker)
        dbSession.commit()

        # создаем WorkerService и загружаем его данные
        workerService = WorkerService(self.application.getResultPath(), worker)
        workerService.load()
        workerService.version = workerService.version + 1
        workerService.init()

        # создаем и запускаем тред
        workerThread = self.createHiveWorker(workerService)
        workerThread.start()

        self.redirect('/dashboard/app/' + app.code + '/')


class ShowNewTaskAction(AjaxController):
    def get(self, *args, **kwargs):
        appcode, workerId = args
        aliveThreadNames = ThredService.getAliveThreads()
        if not 'worker-' + workerId in aliveThreadNames:
            self.renderJSON({'redirect':'status/' + workerId})
        else:
            self.renderJSON({'html': self.render('/dashboard/create/responseOnCreate.jinja2', _return = True), 'vars':{}})