# coding=utf-8
import HadoopService

class ResourceManagerService(HadoopService):
    def __init__(self, rmurl):
        self.rmurl = rmurl

    def getApps(self):
        url = self.rmurl + '/ws/v1/cluster/apps'
        data = self.loadJSON(url)
        print data