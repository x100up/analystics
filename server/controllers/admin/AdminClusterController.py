# coding=utf-8
__author__ = 'pavlenko.roman.spb@gmail.com'

from controllers.admin.AdminIndexController import AdminAction, AdminAjaxAction
from services.ClusterHadoopService import ClusterHadoopService
from datetime import datetime
import time, random

class IndexAction(AdminAction):

    def get(self, *args, **kwargs):
        self.render('admin/cluster/index.jinja2')


class ClusterStateAction(AdminAjaxAction):

    def get(self, *args, **kwargs):
        clusterHadoopService = ClusterHadoopService()
        state = clusterHadoopService.getState('web345.local:8088')

        currentTs = time.mktime(datetime.now().timetuple()) * 1000
        totalUsed = 0
        for rack in state:
            for node in state[rack]:
                totalUsed += int(node['usedMemoryMB'])

        self.render('admin/cluster/state.jinja2', {'state':state, 'currentTs':currentTs, 'totalUsed':int(totalUsed)})