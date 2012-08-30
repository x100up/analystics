import BaseController
import tornado.web

class IndexAction(BaseController.BaseController):

    @tornado.web.authenticated
    def get(self):
        self.redirect('/dashboard')



