# coding=utf-8
__author__ = 'pavlenko.roman.spb@gmail.com'

from controllers.admin.AdminIndexController import AdminAction
import urllib2, re


class IndexAction(AdminAction):
    def get(self, *args, **kwargs):
        self.render('admin/proxy/resourceManager.jinja2')

class HistoryServerAction(AdminAction):
    def get(self, *args, **kwargs):
        url = '/'
        if len(args):
            if args[0]:
                url = args[0]

        src = re.compile('src=\"([^\"]+)\"')
        href = re.compile('href=\"([^\"]+)\"')

        root = 'http://resource.hadoop.pretender.local:8088'
        print 'open {}', format(root + url)
        f = urllib2.urlopen(root + url)
        data = f.read()
        data = src.sub('src="/admin/resourceManager/proxy\\1' + '"', data)
        data = href.sub('href="/admin/resourceManager/proxy\\1' + '"', data)
        self.write(data)
