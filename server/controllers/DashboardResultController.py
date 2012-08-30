# -*- coding: utf-8 -*-
from BaseController import BaseController
from models.Worker import Worker
from service.WorkerService import WorkerService
import tornado, json

class ResultAction(BaseController):

    @tornado.web.authenticated
    def get(self):
        jobId = self.get_argument('jobId')

        db = self.getDBSession()
        worker = db.query(Worker).filter_by(uuid = jobId).first()

        service = WorkerService(self.getConfig('core', 'result_path'), worker)
        result = {
            'chartconf': {
                'subtitle' : {'text' :  'job ' + jobId},
                'title' : { 'text': 'График'},
                'yAxis': { 'title': {'text': 'Количество'}},
            }
        }
        result['data'] = service.getResults()

        self.render('dashboard/result.jinja2', {'js_vars': json.dumps(result)})