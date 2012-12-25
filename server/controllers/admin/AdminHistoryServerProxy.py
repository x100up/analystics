# coding=utf-8
__author__ = 'pavlenko.roman.spb@gmail.com'

from controllers.admin.AdminIndexController import AdminAction
import urllib2


class IndexAction(AdminAction):
    def get(self, *args, **kwargs):
        self.render('admin/proxy/historyServer.jinja2')

class HistoryServerAction(AdminAction):
    def get(self, *args, **kwargs):
        print args
        root = 'http://historyserver.hadoop.pretender.local:19888'

        f = urllib2.urlopen(root)
        data = f.read()
        self.write(data)
