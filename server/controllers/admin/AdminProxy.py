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
        href = re.compile('href=\"([^\"]+)\"')

        f = urllib2.urlopen('http://{}:{}{}'.format(host, port, url))
        data = f.read()
        data = src.sub('src="/admin/proxy/' + host + '/' + port + '/\\1' + '"', data)
        data = href.sub('href="/admin/proxy/' + host + '/' + port + '/\\1' + '"', data)

        self.write(data)
