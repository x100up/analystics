# -*- coding: utf-8 -*-
from components.ChartConstructor import ChartConstructor
from components.TableConstructor import TableConstructor
from controllers.BaseController import AjaxController
from models.Worker import Worker
from models.App import App
from services.AppService import AppService
from services.RuleService import RuleService
from services.WorkerService import WorkerService
from components.NameConstructor import NameConstructor
import tornado
import time
import tornado.web


class BaseResultAction(AjaxController):

    def prepare(self):
        super(AjaxController, self).prepare()
        self.dbSession = self.getDBSession()

    def getWorker(self, workerId):
        return self.dbSession.query(Worker).filter_by(workerId = int(workerId)).first()


class ResultAction(BaseResultAction):

    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        # get app code
        if len(args) == 0:
            raise RuntimeError('Cant find app code in dashboard')
        appCode = args[0]

        user = self.get_current_user()

        # get app
        app = self.dbSession.query(App).filter(App.code == appCode).first()
        if app is None:
            raise RuntimeError('Cant find app by code ' + appCode)

        # check access
        ruleService = RuleService(self.dbSession)
        if not ruleService.isAllow(user.userId, app.appId):
            raise RuntimeError('Access denied')

        workerId = self.get_argument('jobId')

        worker = self.getWorker(workerId)
        service = WorkerService(self.application.getResultPath(), worker)

        if worker.status != Worker.STATUS_SUCCESS:
            self.renderJSON({'redirect': 'status/' + str(workerId)})
            return

        # configuration name services
        task = service.getTask()

        startDates = []
        endDates = []
        for i in task.items:
            taskItem = task.items[i]
            startDates.append(taskItem.start)
            endDates.append(taskItem.end)

        minStartDate = min(startDates)
        maxEndDate = max(endDates)

        appService = AppService(self.application.getAppConfigPath())
        appConfig = appService.getNewAppConfig(app.code)
        nameService = NameConstructor(appConfig, task)

        try:
            data = service.getResultData()['data']['result']
            if len(data.items()) == 0:
                self.render('dashboard/result_no_data.jinja2', {'app': app})
                return
            # chart data
            chartService = ChartConstructor(data, nameService, task)
            tableService = TableConstructor(data, nameService, task)
        except IOError as ioerr:
            self.render('dashboard/result.jinja2', {'errors': [u'Ошибка чтения результатов выполнения работы'], 'app': app})
        else:
            html = self.render('dashboard/result.jinja2',
                    {'app': app, 'data':data, 'tablesdata': tableService.getData(), 'nameService':nameService,
                     'chartService':chartService, 'name': worker.name, 'interval':task.interval, 'tagCloud':chartService.getTagCloud(), 'workerId':workerId}, _return = True)

            self.renderJSON({'html': html, 'vars': {
                'chartdata': chartService.getResult(),
                'interval': task.interval,
                'minStartDate': time.mktime(minStartDate.timetuple()),
                'maxEndDate': time.mktime(maxEndDate.timetuple()),
                'taskId': workerId
            }})


class TableAction(BaseResultAction):
    def get(self, *args, **kwargs):
        appCode, taskId = args
        worker = self.getWorker(int(taskId))
        service = WorkerService(self.application.getResultPath(), worker)
        data = service.getResultData()['data']['result']

        task = service.getTask()

        appService = AppService(self.application.getAppConfigPath())
        appConfig = appService.getNewAppConfig(appCode)
        nameService = NameConstructor(appConfig, task)

        tableService = TableConstructor(data, nameService, task)
        tableHeaders, tableData = tableService.getVerticalData()
        self.render('dashboard/result/table2.jinja2', tableData=tableData, tableHeaders=tableHeaders,
                    interval=task.interval)


class ShowTaskStatus(BaseResultAction):
    def get(self, *args, **kwargs):
        appCode, workerId = args
        worker = self.getWorker(workerId)

        if worker.status == Worker.STATUS_ALIVE:
            self.renderJSON({'html': self.render('dashboard/result/taskAlive.jinja2', _return=True) })
        elif (worker.status == Worker.STATUS_ERROR) or (worker.status == Worker.STATUS_DIED):
            service = WorkerService(self.application.getResultPath(), worker)
            self.renderJSON({'html': self.render('dashboard/result/taskFailed.jinja2', {'errors': [service.getError()]}, _return=True) })
        elif worker.status == Worker.STATUS_SUCCESS:
            self.renderJSON({'redirect': 'result/job=' + workerId })
        else:
            raise Exception('Unknown worker state')

