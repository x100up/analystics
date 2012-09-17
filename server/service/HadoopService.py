# coding=utf-8
import urllib2
import json

class HadoopService():
    def loadJSON(self, url):
        req = urllib2.Request(url)
        opener = urllib2.build_opener()
        f = opener.open(req)
        return json.load(f)