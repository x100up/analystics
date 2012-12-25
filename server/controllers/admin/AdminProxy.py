# coding=utf-8
__author__ = 'pavlenko.roman.spb@gmail.com'

from controllers.admin.AdminIndexController import AdminAction
import urllib2, re


class ResourceManagerView(AdminAction):
    def get(self, *args, **kwargs):
        self.render('admin/proxy/resourceManager.jinja2')

class CoreProxy(AdminAction):

    def get(self, host, port, url = '/'):
        src = re.compile('src=\"([^\"]+)\"')
        href = re.compile('href=\"/([^\"]+)\"')
        abshref = re.compile('href=\"http://([^\:]+)\:(\d+)([^\"]+)\"')

        if url == None:
            url = '/'

        f = urllib2.urlopen('http://{}:{}{}'.format(host, port, url))
        data = f.read()
        data = src.sub('src="/admin/proxy/' + host + '/' + port + '/\\1' + '"', data)
        data = href.sub('href="/admin/proxy/' + host + '/' + port + '//\\1' + '"', data)
        data = abshref.sub('href="/admin/proxy/\\2/\\3//\\1' + '"', data)


        #/admin/proxy/resource.hadoop.pretender.local/8088/http://web345:8042/node/containerlogs/container_1356430503316_0001_01_000001/hive

        self.write(data)
