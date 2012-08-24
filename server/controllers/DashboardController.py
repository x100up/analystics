# -*- coding: utf-8 -*-
from BaseController import BaseController
from service.HiveService import createHiveQuery
from worker import HiveWorker
from models.Worker import Worker
import uuid, tornado.web
from datetime import datetime
from service.WorkerService import WorkerService
from sqlalchemy import desc
from service import ThredService

class IndexAction(BaseController):

    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        session = self.getDBSession()

        # получаем список последних запросов
        lastWorkers = session.query(Worker).filter_by(userId = user.userId).order_by(desc(Worker.startDate)).limit(10)
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
                session.add(worker)

        session.commit()
        self.render('dashboard/dashboard.jinja2', {'lastWorkers' : workers})

class CreateAction(BaseController):
    """
        Добавление новой задачи
    """
    @tornado.web.authenticated
    def get(self):

        self.render('dashboard/new.jinja2')

    def post(self):
        start = self.get_argument('start', False)
        start = datetime.strptime(start, "%m/%d/%Y %H:%M")

        end = self.get_argument('end', False)
        end = datetime.strptime(end, "%m/%d/%Y %H:%M")

        group_interval = self.get_argument('group_interval', False)
        appname = self.get_argument('appname', False)

        query = createHiveQuery(appname, start, end, group_interval = group_interval)
        print self.request.arguments
        self.write(query)


class HiveAction(BaseController):
    '''
    Запуск воркера на Hive
    '''
    @tornado.web.authenticated
    def get(self):
        # создаем новый запрос к hive
        query = "SELECT count(1) FROM topface.stat_KEY_1"

        user = self.get_current_user()

        worker = Worker()
        worker.uuid = str(uuid.uuid4())
        worker.userId = user.userId
        worker.startDate = datetime.now()
        worker.status = Worker.STATUS_ALIVE

        ws = WorkerService(self.getConfig('core', 'result_path'))
        ws.initWorker(worker)
        session = self.getDBSession()
        session.add(worker)
        session.commit()

        print 'create worker ' + worker.uuid

        # тут будем констуровать запрос
        workerThread = HiveWorker.HiveWorker(query)
        # передает sessionmaker т.к. он создает сеессию в пределах треда
        workerThread.mysqlSessionMaker = self.getSessionMaker()
        workerThread.folderForWorkerService = self.getConfig('core', 'result_path')
        workerThread.setName(worker.uuid)
        workerThread.start()

        self.redirect("/dashboard?newJob=" + str(worker.uuid))