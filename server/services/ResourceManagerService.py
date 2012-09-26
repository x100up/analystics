# coding=utf-8
from HadoopService import HadoopService
import re
from pprint import  pprint

class ResourceManagerService(HadoopService):
    def __init__(self, rmurl):
        self.rmurl = rmurl
        self.appCache = None

    def getApps(self, state = None):
        url = self.rmurl + '/ws/v1/cluster/apps'
        if state:
            url += '?state=' + state
        return self.loadJSON(url)

    def getWorkerProgresses(self, workerIDs):
        result = []
        if self.appCache is None:
            self.appCache = self.getApps(state = 'RUNNING')
        apps = self.appCache
        if apps['apps']:
            for app in apps['apps']['app']:
                workerId, stage, progress = self.getAppData(app)
                if workerId in workerIDs:
                    result.append( (workerId, stage, progress) )
        return result

    workerIdRe = re.compile('^SELECT \'(\d+)\' as `wid`(.*)\(Stage-(\d+)\)$')

    def getAppData(self, app):
        matchObject = self.workerIdRe.search(app['name'])
        if matchObject:
            return (int(matchObject.group(1)), int(matchObject.group(3)), app['progress'])
