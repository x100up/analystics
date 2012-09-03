# -*- coding: utf-8 -*-
from BaseController import BaseController
from service.QueryService import HiveQueryConstructor
from worker import HiveWorker
from models.Worker import Worker
from models.Task import Task, TaskItem
import uuid, tornado.web
from datetime import datetime, timedelta
from service.WorkerService import WorkerService
from sqlalchemy import desc
from service import ThredService
from models.UserAppRule import RuleCollection
from sqlalchemy import func
import math

class SwitchApp(BaseController):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        user = self.get_current_user()
        rc = RuleCollection(self.getDBSession())
        apps = rc.getUserApps(user.userId)
        if len(apps) == 0:
            self.redirect("/dashboard/empty")
        elif len(apps) == 1:
            self.redirect("/dashboard/app/" + apps[0].code + '/')
        else:
            self.redirect("/dashboard/selectapp")


class IndexAction(BaseController):

    def post(self, appName):
        self.get(appName)

    @tornado.web.authenticated
    def get(self, appName):

        app = self.checkAppAccess(appName)

        # get user and db session
        user = self.get_current_user()
        db_session = self.getDBSession()

        action = self.get_argument('action', False)
        if action == u'Удалить':
            uuids = self.get_arguments('jobId', False)
            if uuids:
                workers = db_session.query(Worker).filter(Worker.uuid.in_(uuids)).all()
                for worker in workers:
                    try:
                        WorkerService(self.getConfig('core', 'result_path'), worker).delete()
                    except OSError as oserror:
                        print oserror
                        pass
                    db_session.delete(worker)


        perPage = 10

        # получаем количество
        count, = db_session.query(func.count(Worker.uuid)).filter(Worker.userId == user.userId, Worker.appId == app.appId).first()
        pageCount = int(math.ceil(float(count) / 10))
        page = int(self.get_argument('page', 1))

        # получаем список последних запросов
        lastWorkers = db_session.query(Worker).filter(Worker.userId == user.userId, Worker.appId == app.appId).order_by(desc(Worker.startDate)).offset(perPage * (page - 1)).limit(perPage)

        workers = []
        alivedWorkers= []
        for worker in lastWorkers:
            if worker.status == Worker.STATUS_ALIVE:
                alivedWorkers.append(worker)

            workers.append(worker)

        aliveThreadNames = ThredService.getAliveThreads()
        for worker in alivedWorkers:
            if not worker.uuid in aliveThreadNames:
                worker.status = Worker.STATUS_DIED
                db_session.add(worker)

        db_session.commit()
        self.render('dashboard/dashboard.jinja2', {'lastWorkers' : workers, 'app':app, 'pageCount':pageCount, 'currentPage': page})

class EmptyAppAction(BaseController):
    @tornado.web.authenticated
    def get(self):
        self.render('dashboard/emptyApps.jinja2')

class SelectAppAction(BaseController):
    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        rc = RuleCollection(self.getDBSession())
        apps = rc.getUserApps(user.userId)
        self.render('dashboard/selectApp.jinja2', {'apps':apps})

class CreateAction(BaseController):
    """
        Добавление новой задачи
    """
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        app = self.checkAppAccess(args)

        taksItem = TaskItem(delta = timedelta(days = -1))
        taksItem.index = 1

        task = Task(appname = app.code)
        task.addTaskItem(taksItem)

        self.render('dashboard/new.jinja2', {'task':task, 'app':app})

    def post(self, *args, **kwargs):
        app = self.checkAppAccess(args)

        start = self.get_argument('start', False)
        start = datetime.strptime(start, "%m/%d/%Y %H:%M")

        end = self.get_argument('end', False)
        end = datetime.strptime(end, "%m/%d/%Y %H:%M")

        appname = self.get_argument('appname', False)
        group_interval = self.get_argument('group_interval', False)

        task = Task(start = start, end = end, appname = appname, interval = group_interval)

        # parse keys and tags
        keys =  self.get_arguments('key')
        index = 1
        for key in keys:
            tags = self.get_arguments('tag_' + str(index) + '_name')
            for tag in tags:
                tagsValue = self.get_arguments('tag_' + str(index) + '_' + tag, None)
                task.addCondition(key, tag, tagsValue)
            index += 1

        constructor = HiveQueryConstructor(task)
        query = constructor.getHiveQuery()
        user = self.get_current_user()

        # объект для записи в базу
        worker = Worker()
        worker.uuid = str(uuid.uuid4())
        worker.userId = user.userId
        worker.startDate = datetime.now()
        worker.status = Worker.STATUS_ALIVE
        session = self.getDBSession()
        session.add(worker)
        session.commit()

        # создаем WorkerService - он будет связывать тред с файловой системой
        workerService = WorkerService(self.getConfig('core', 'result_path'), worker)
        workerService.setQuery(query)
        workerService.setFields(constructor.getFields())
        workerService.init()

        # тут будем констуровать запрос
        workerThread = HiveWorker.HiveWorker(workerService)
        # передает sessionmaker т.к. он создает сеессию в пределах треда
        workerThread.mysqlSessionMaker = self.getSessionMaker()
        workerThread.folderForWorkerService = self.getConfig('core', 'result_path')
        workerThread.host = self.getConfig('hive', 'host')
        workerThread.host = self.getConfig('hive', 'port')
        workerThread.setName(worker.uuid)
        workerThread.start()

        self.write(query)

        #self.redirect("/dashboard?newJob=" + str(worker.uuid))

