import BaseController
import tornado.web

class IndexAction(BaseController.BaseController):
    @tornado.web.authenticated
    def get(self):
        myThreads = []
        self.write(self.getTemplate('page/index.jinja2').render(myThreads = myThreads))


