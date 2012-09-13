# -*- coding: utf-8 -*-
from controllers.BaseController import BaseController
from models.Worker import Worker
import tornado.web, math
from service.WorkerService import WorkerService
from sqlalchemy import desc
from service import ThredService
from models.UserAppRule import RuleCollection
from sqlalchemy import func

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
                        WorkerService(self.application.getResultPath(), worker).delete()
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



