# coding=utf-8
__author__ = 'pavlenko.roman.spb@gmail.com'

from services.HadoopService import HadoopService
import json

class ClusterHadoopService(HadoopService):

    def getState(self, clusterHost):
        #data =  json.loads('{"nodes":{"node":[{"rack":"/default-rack","state":"RUNNING","id":"web345:44826","nodeHostName":"web345","nodeHTTPAddress":"web345:8042","healthStatus":"Healthy","lastHealthUpdate":1355993991777,"healthReport":"","numContainers":0,"usedMemoryMB":0,"availMemoryMB":8192},{"rack":"/default-rack","state":"RUNNING","id":"web346:48369","nodeHostName":"web346","nodeHTTPAddress":"web346:8042","healthStatus":"Healthy","lastHealthUpdate":1355993943481,"healthReport":"","numContainers":0,"usedMemoryMB":0,"availMemoryMB":8192},{"rack":"/default-rack","state":"RUNNING","id":"web347:47280","nodeHostName":"web347","nodeHTTPAddress":"web347:8042","healthStatus":"Healthy","lastHealthUpdate":1355993943044,"healthReport":"","numContainers":0,"usedMemoryMB":0,"availMemoryMB":8192}]}}')

        data = self.loadJSON('http://' + clusterHost + '/ws/v1/cluster/nodes')

        result = {}

        for node in data['nodes']['node']:
            rack = node['rack']
            if not result.has_key(rack):
                result[rack] = []

            result[rack].append(
                node
            )

        return result