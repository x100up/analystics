# -*- coding: utf-8 -*-
from controllers.BaseController import AjaxController
from services.AppService import AppService
from models.Task import TaskItem
from models.Worker import Worker
from services import ThredService
from components.TaskFactory import createTaskFromRequestArguments
from models.appConf.AppEvent import AppEvent
from models.appConf.AppTag import AppTag
from models.appConf.AppTagBunch import AppTagBunch
from components.NameConstructor import NameConstructor
import random

class KeyConfigurationAction(AjaxController):

    def post(self, *args, **kwargs):
        eventCode = self.get_argument('eventCode', None)
        appCode = self.get_argument('appCode', None)
        index = self.get_argument('index', 1)

        taskItem = TaskItem(index = index, key = eventCode)

        appService = AppService(self.application.getAppConfigPath())
        appConfig = appService.getNewAppConfig(appCode)

        nameConstructor = NameConstructor(appConfig)
        taskItem.name = nameConstructor.getTaskItemName(taskItem)

        self.render('dashboard/taskForm/eventFormItem.jinja2', {
            'taskItem': taskItem,
            'appConfig': appConfig,
            'values':{

            }
        })

class GetKeyForm(AjaxController):
    def post(self, *args, **kwargs):
        appCode = self.get_argument('appCode')
        index = self.get_argument('index')
        taskItem = TaskItem(index = index)
        self.render('dashboard/taskForm/eventFormItem.jinja2', {'taskItem':taskItem})

class SaveWorkerName(AjaxController):
    def post(self):
        session = self.getDBSession()
        worker = session.query(Worker).filter(Worker.workerId == int(self.get_argument('workerId'))).first()
        worker.name = self.get_argument('name')
        session.add(worker)
        session.commit()
        self.renderJSON({'status':'ok'})

class AddNewKey(AjaxController):
    def post(self):
        data = {
            'index': self.get_argument('index'),
            'event': AppEvent(),
        }
        self.render('admin/appConfig/editOneEvent.jinja2', data)

class AddNewTag(AjaxController):
    def post(self):
        data = {
            'index': self.get_argument('index'),
            'tag': AppTag(),
        }
        self.render('admin/appConfig/editOneTag.jinja2', data)

class AddNewBunch(AjaxController):
    def post(self, *args, **kwargs):
        appCode = self.get_argument('appCode')
        appService = AppService(self.application.getAppConfigPath())
        appConfig = appService.getNewAppConfig(appCode)
        data = {
            'index': self.get_argument('index'),
            'bunch': AppTagBunch(),
            'tags': appConfig.getTags()
        }
        self.render('admin/appConfig/editOneBunch.jinja2', data)

class GatTasksProgress(AjaxController):
    def post(self, *args, **kwargs):
        arguments = []
        appIdToWorkerId = {}
        blank = u'None'

        for workerId, stageCount in self.request.arguments.items():
            arguments.append( (int(workerId), stageCount) )

        #resourceManagerService = ResourceManagerService(self.getConfigValue(Config.HADOOP_YARN_RESOURCEMANAGER))

        # получаем прогресс задач
        #progressResult = None
        #diedWorkers = []
        #
        #if toGetProgress:
        #    progressResult = resourceManagerService.getWorkerProgresses(toGetProgress)


        diedWorkers = []
        workerIds = [workerId for workerId, stageCount in arguments]
        aliveThreadNames = ThredService.getAliveThreads()
        for workerId in workerIds:
            if not 'worker-' + str(workerId) in aliveThreadNames:
                diedWorkers.append(workerId)

        workerStates = []
        if diedWorkers:
            db = self.getDBSession()
            workerStates = db.query(Worker.workerId, Worker.status).filter(Worker.workerId.in_(diedWorkers)).all()
        self.renderJSON({'workerStates':workerStates})


class CopyTaskKey(AjaxController):
    '''
    remote copy task key
    '''
    def post(self, *args, **kwargs):
        copy_index = self.get_argument('copy_key_index')
        new_index = self.get_argument('new_index')
        appCode = self.get_argument('appname')
        task = createTaskFromRequestArguments(self.request.arguments)
        taskItem = task.getTaskItem(copy_index)
        taskItem.index = new_index
        appService = AppService(self.application.getAppConfigPath())
        appConfig = appService.getNewAppConfig(appCode)
        self.render('dashboard/taskForm/eventFormItem.jinja2', {'taskItem': taskItem, 'appConfig':appConfig})


class getTemplateModal(AjaxController):
    def get(self, *args, **kwargs):
        self.render('dashboard/template/templatemodal.jinja2')




class DownloadCSVAction(AjaxController):
    def post(self, *args, **kwargs):
        rows = []
        i = 0
        while True:
            k = 'data[{}][]'.format(i)
            if self.request.arguments.has_key(k):
                rows.append(';'.join( self.get_arguments(k, strip=False)) )
                i = i + 1
            else:
                break

        index = random.randint(0, 1566666)
        self.application.setData(index, "\n".join(rows))
        self.write(str(index))

    def get(self, *args, **kwargs):
        index = int(self.get_argument('file'))
        self.set_header('Content-Type', 'text/csv')
        self.set_header('Content-Disposition', 'attachment; filename="data{}.csv"'.format(index))
        self.set_header('Cache-Control', 'no-cache, must-revalidate')
        self.set_header('Pragma', 'no-cache')

        self.write(self.application.getData(index))
        self.application.deleteData(index)

from datetime import datetime, timedelta

def toDate(strDate):
    year, month, date, hour, minutes = strDate.split('-')
    return datetime(int(year), int(month), int(date), int(hour), int(minutes))


class GetDateSelector(AjaxController):

    def get(self, *args, **kwargs):


        index = self.get_argument('index')

        showDelta = timedelta(days = 60)

        now = datetime.now()
        start = toDate(self.get_argument('start'))
        end = toDate(self.get_argument('end'))

        startWith = self.get_argument('startWith', None)
        if startWith:
            year, month, day = startWith.split('-')
            startWith = datetime(int(year), int(month), int(day))
        else:
            startWith = now
            if end - start < showDelta:
                if end + timedelta(days = 30) > now:
                    startWith = (end - timedelta(days = end.day + 1)).replace(day = 1, hour=0, minute=0, second=0, microsecond=0)
                    print startWith
            else:
                pass


        endWith = startWith
        for i in range(0, 2):
            if endWith.month == 12:
                endWith = endWith.replace(year = endWith.year + 1, month = 1)
            else:
                endWith = endWith.replace(month = endWith.month + 1)


        dates = []
        _startWith = startWith
        while _startWith < endWith:
            dates.append(_startWith)
            _startWith = _startWith + timedelta(days = 1)

        if startWith.month == 1:
            prevMonth = startWith.replace(year = startWith.year - 1, month=12)
        else:
            prevMonth = startWith.replace(month = startWith.month - 1)
            print

        if startWith.month == 12:
            nextMonth = startWith.replace(year = startWith.year + 1, month=1)
        else:
            nextMonth = startWith.replace(month = startWith.month + 1)

        print start, '-', end

        self.render('dashboard/taskForm/dateSelector.jinja2',
            {
                'start': start,
                'end': end,
                'dates': dates,
                'prevMonth': prevMonth,
                'nextMonth': nextMonth,
                'index': index,
                'isOneDay': start.date() == (end - timedelta(days = 1)).date()
            })


