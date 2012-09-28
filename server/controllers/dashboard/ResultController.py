# -*- coding: utf-8 -*-
from components.ChartConstructor import ChartConstructor
from controllers.BaseController import BaseController
from models.Worker import Worker
from models.App import App
from services.AppService import AppService
from services.RuleService import RuleService
from services.WorkerService import WorkerService
from components.NameConstructor import NameConstructor
import tornado, json

class ResultAction(BaseController):

    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        # get app code
        if len(args) == 0:
            raise RuntimeError('Cant find app code in dashboard')
        appCode = args[0]

        dbSession = self.getDBSession()
        user = self.get_current_user()

        # get app
        app = dbSession.query(App).filter(App.code == appCode).first()
        if app is None:
            raise RuntimeError('Cant find app by code ' + appCode)

        # check access
        ruleService = RuleService(dbSession)
        if not ruleService.isAllow(user.userId, app.appId):
            raise RuntimeError('Access denied')

        workerId = self.get_argument('jobId')

        worker = dbSession.query(Worker).filter_by(workerId = workerId).first()
        service = WorkerService(self.application.getResultPath(), worker)

        if worker.status == Worker.STATUS_ALIVE:
            self.redirect('/')
            return
        elif worker.status == Worker.STATUS_DIED or worker.status == Worker.STATUS_ERROR:
            self.render('dashboard/task_failed.jinja2', {'errors': [service.getError()]})
            return

        # configuration name services
        task = service.getTask()
        appService = AppService(self.application.getAppConfigPath())
        appConfig = appService.getAppConfig(app.code)
        nameService = NameConstructor(appConfig, task)


        try:
            data = service.getResults()
            # chart data
            chartService = ChartConstructor(data, nameService)
        except IOError as ioerr:
            self.render('dashboard/result.jinja2', {'errors': [u'Ошибка чтения результатов выполнения работы'], 'app': app})
        else:
            self.render('dashboard/result.jinja2', {'js_vars': json.dumps(chartService.getResult()), 'app': app, 'data':data, 'nameService':nameService})