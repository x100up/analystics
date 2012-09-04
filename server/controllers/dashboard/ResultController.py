# -*- coding: utf-8 -*-
from controllers.BaseController import BaseController
from models.Worker import Worker
from models.App import App
from service.RuleService import RuleService
from service.WorkerService import WorkerService
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
        result = {
            'chartconf': {
                'subtitle' : {'text' :  'job ' + jobId},
                'title' : { 'text': 'График'},
                'yAxis': { 'title': {'text': 'Количество'}},
            }
        }

        try:
            result['data'] = service.getResults()
        except IOError as ioerr:
            self.render('dashboard/result.jinja2', {'errors': [u'Ошибка чтения результатов выполнения работы'], 'app': app})
        else:
            self.render('dashboard/result.jinja2', {'js_vars': json.dumps(result), 'app': app})