# -*- coding: utf-8 -*-
from __builtin__ import len
from components import HiveWorker
from components.HiveQueryConstructor import  HiveQueryConstructor
from controllers.BaseController import BaseController, AjaxController
from models.Worker import Worker
from models.Task import Task
from datetime import datetime
from services.WorkerService import WorkerService
from services.AppService import AppService
from components.TaskFactory import createTaskFromRequestArguments
from components.NameConstructor import NameConstructor
from models.TaskTemplate import TaskTemplate, TaskTemplateFile
from sqlalchemy.sql import or_, and_
import tornado.web
from services import ThredService


class CreateTaskController(BaseController):

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
        appService = AppService(self.application.getAppConfigPath())
        appConfig = appService.getNewAppConfig(app.code)
        dbSession = self.getDBSession()
        baseTask = self.get_argument('baseOn', False)
        template = self.get_argument('template', False)
        nameConstructor = NameConstructor(appConfig)
        if baseTask:
            # задача основана на другой задаче
            worker = dbSession.query(Worker).filter_by(workerId = baseTask).first()
            workerService = WorkerService(self.application.getResultPath(), worker)
            task = workerService.getTask()
            # fix indexes
            for index, taskItem in enumerate(task.getTaskItems()):
                taskItem.index = index
                if not taskItem.name:
                    taskItem.name = nameConstructor.getTaskItemName(taskItem)

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
            task = Task(appname = app.code)

        eventsLoaded = len(task.items)



        html = self.render('dashboard/new.jinja2', {'task':task, 'app':app,  'appConfig':appConfig}, _return = True)

        self.renderJSON({'html': html, 'vars':{'eventLoaded': eventsLoaded}})

    def post(self, *args, **kwargs):
        app = self.checkAppAccess(args)

        saveAsTemplate = str(self.get_argument('saveAsTemplate', default=''))

        # создаем задачу из аргументов
        task = createTaskFromRequestArguments(self.request.arguments)
        session = self.getDBSession()

        if saveAsTemplate:
            # сохраняем шаблон
            taskTemplate = TaskTemplate()
            taskTemplate.appId = app.appId
            taskTemplate.name = self.get_argument('taskName', default = None)
            taskTemplate.userId = self.get_current_user().userId
            taskTemplate.shared =  TaskTemplate.SHARED_NO

            session.add(taskTemplate)
            session.commit()

            # скидываем на диск
            taskTemplateFile = TaskTemplateFile(self.application.getTemplatePath(), task = task, taskTemplate = taskTemplate)
            taskTemplateFile.baseDate = datetime.now()
            taskTemplateFile.save()

            self.redirect('/dashboard/app/{}/#templates'.format(app.code))
            return

        user = self.get_current_user()

        # объект для записи в базу
        worker = Worker()
        worker.userId = user.userId
        worker.startDate = datetime.now()
        worker.status = Worker.STATUS_ALIVE
        worker.appId = app.appId
        worker.name = self.get_argument('taskName', default=None)

        # генерируем имя запроса
        appService = AppService(self.application.getAppConfigPath())
        appConfig = appService.getAppConfig(app.code)
        nameConstructor = NameConstructor(appConfig, task)
        if not worker.name:
            worker.name = nameConstructor.generateTaskName()

        session.add(worker)
        session.commit()

        # конструирем запрос
        constructor = HiveQueryConstructor(task, appConfig)
        query = constructor.getHiveQuery(worker.workerId)

        self.write(query)
        return
        #task.stageCount = constructor.getStageCount()
        # создаем WorkerService - он будет связывать тред с файловой системой
        workerService = WorkerService(self.application.getResultPath(), worker)
        workerService.setQuery(query)
        workerService.setTask(task)
        workerService.init()

        # создаем и запускаем тред
        workerThread = self.createHiveWorker(workerService)
        workerThread.start()

        self.redirect('/dashboard/app/' + app.code + '/#new_task/' + str(worker.workerId))

class RecalculateAction(CreateTaskController):

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
            self.renderJSON({'html': self.render('/dashboard/result/taskAlive.jinja2', _return = True)})
