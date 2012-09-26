# coding=utf-8
from HadoopService import HadoopService
import re

class ResourceManagerService(HadoopService):
    def __init__(self, rmurl):
        self.rmurl = rmurl
        self.appCache = None

    def getApps(self):
        url = self.rmurl + '/ws/v1/cluster/apps'
        return self.loadJSON(url)


    def getAppIdsForWorkers(self, workerIdList):
        result = []
        if self.appCache is None:
            self.appCache = self.getApps()
        apps = self.appCache
        if apps.has_key('apps'):
            for app in apps['apps']['app']:
                workerId = self.parseWorkerId(app['name'])
                if workerId and int(workerId) in workerIdList:
                    result.append( ( int(workerId), app['id'] ) )
        return result

    workerIdRe = re.compile('^SELECT \'(\d+)\' as `wid`')

    def getAppProgresses(self, appIdList):
        result = []
        if self.appCache is None:
            self.appCache = self.getApps()
        apps = self.appCache
        for app in apps['apps']['app']:
            appId = app['id']
            if appId in appIdList:
                result.append( ( appId, app['progress'] ) )
        return result

    def parseWorkerId(self, app_name):
        matchObject = self.workerIdRe.search(app_name)
        if matchObject:
            return matchObject.group(1)

