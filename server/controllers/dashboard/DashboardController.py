# -*- coding: utf-8 -*-
import tornado.web
import math

from controllers.BaseController import BaseController
from models.Worker import Worker
from services.WorkerService import WorkerService
from sqlalchemy import desc
from services import ThredService
from models.UserAppRule import RuleCollection
from sqlalchemy import func

class BaseDashboardAction(BaseController):
    def getWorkerList(self, app, page = 1):
        db_session = self.getDBSession()
        user = self.get_current_user()
        perPage = 5
        # получаем количество
        count, = db_session.query(func.count(Worker.workerId)).filter(Worker.userId == user.userId, Worker.appId == app.appId).first()
        pageCount = int(math.ceil(float(count) / perPage))
        # получаем список последних запросов
        lastWorkers = db_session.query(Worker).filter(Worker.userId == user.userId, Worker.appId == app.appId).order_by(desc(Worker.startDate)).offset(perPage * (page - 1)).limit(perPage)

        # определяем, какие воркеры уже умерли
        workers = []
        alivedWorkers= []
        for worker in lastWorkers:
            if worker.status == Worker.STATUS_ALIVE:
                alivedWorkers.append(worker)

            workers.append(worker)

        aliveThreadNames = ThredService.getAliveThreads()
        for worker in alivedWorkers:
            # определяем мертвые воркеры
            if not 'worker-' + str(worker.workerId) in aliveThreadNames:
                worker.status = Worker.STATUS_DIED
                db_session.add(worker)
                alivedWorkers.remove(worker)

        db_session.commit()

        # для живых воркеров загружаем таски
        if alivedWorkers:
            workerService = WorkerService(self.application.getResultPath())
            for worker in alivedWorkers:
                workerService.setWorker(worker)
                worker.task = workerService.getTask()
        return workers, pageCount

    def getPager(self, pageCount, page):
        startPageRange = 1
        endPageRange = pageCount
        return (startPageRange, endPageRange)



class FirstAction(BaseDashboardAction):

    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        app = self.checkAppAccess(args)
        self.render('dashboard/first/first.jinja2', {'app':app})

class SwitchApp(BaseDashboardAction):
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

    def post(self, *args, **kwargs):
        appCode = self.get_argument('appCode')
        self.redirect("/dashboard/app/" + appCode + '/')


class IndexAction(BaseDashboardAction):
    def post(self, appName):
        self.get(appName)

    @tornado.web.authenticated
    def get(self, appName):
        app = self.checkAppAccess(appName)

        db_session = self.getDBSession()

        action = self.get_argument('action', False)
        print action
        if action == u'Удалить выбранные отчеты':
            workerIds = self.get_arguments('jobId', False)
            if workerIds:
                workers = db_session.query(Worker).filter(Worker.workerId.in_(workerIds)).all()
                for worker in workers:
                    db_session.delete(worker)
                    print worker

            db_session.commit()

        page = int(self.get_argument('page', 1))

        workers, pageCount = self.getWorkerList(app, page)

        startPageRange, endPageRange = self.getPager(pageCount, page)


        self.render('dashboard/dashboard.jinja2', {'lastWorkers' : workers,
                                                   'app':app,
                                                   'pageRange':  range(startPageRange, endPageRange),
                                                   'currentPage': page,
                                                   'js_vars': {'app': app.code}})

class EmptyAppAction(BaseDashboardAction):
    @tornado.web.authenticated
    def get(self):
        self.render('dashboard/emptyApps.jinja2')

class SelectAppAction(BaseDashboardAction):
    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        rc = RuleCollection(self.getDBSession())
        apps = rc.getUserApps(user.userId)
        self.render('dashboard/selectApp.jinja2', {'apps':apps})


class GetWorkers(BaseDashboardAction):

    def get(self, *args, **kwargs):
        app, page = args
        app = self.checkAppAccess(app)

        page = int(page)
        workers, pageCount = self.getWorkerList(app, page)
        startPageRange, endPageRange = self.getPager(pageCount, page)
        self.render('dashboard/workerList.jinja2', {'lastWorkers' : workers,
                                                   'app':app,
                                                   'pageRange':  range(startPageRange, endPageRange),
                                                   'currentPage': page})



