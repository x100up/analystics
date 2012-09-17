import urllib2
import json
import HadoopService

class NameNodeService():

    def __init__(self, namenodeurl):
        self.namenodeurl = namenodeurl

    def load(self):
        req = urllib2.Request(self.namenodeurl + '/jmx')
        opener = urllib2.build_opener()
        f = opener.open(req)
        data = json.load(f)
        if not data.has_key('beans'):
            return None

        new = {}
        for el in data['beans']:
            new[el['name']] = el

        del data
        return new


