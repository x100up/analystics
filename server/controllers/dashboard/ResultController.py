# -*- coding: utf-8 -*-
from controllers.BaseController import BaseController
from models.Worker import Worker
from models.App import App
from service.AppService import AppService, AppNameService
from service.RuleService import RuleService
from service.WorkerService import WorkerService
from service.ChartService import ChartService
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

        jobId = self.get_argument('jobId')

        worker = dbSession.query(Worker).filter_by(uuid = jobId).first()
        service = WorkerService(self.getConfig('core', 'result_path'), worker)


        # configuration name service
        task = service.getTask()
        appService = AppService(self.getConfig('core', 'app_config_path'))
        appConfig = appService.getAppConfig(app.code)
        nameService = AppNameService(appConfig, task)


        try:
            data = service.getResults()
            # chart data
            chartService = ChartService(data, nameService)
        except IOError as ioerr:
            self.render('dashboard/result.jinja2', {'errors': [u'Ошибка чтения результатов выполнения работы'], 'app': app})
        else:
            self.render('dashboard/result.jinja2', {'js_vars': json.dumps(chartService.getResult()), 'app': app, 'data':data, 'nameService':nameService})