__author__ = 'prog-31'
import json
from service.AppService import AppService

from controllers.BaseController import BaseController

class PutConfigAction(BaseController):

    def post(self, *args, **kwargs):
        jsonData = self.get_argument('data', False)
        if jsonData:
            try:
                data = json.loads(jsonData)
                service = AppService(self.getConfig('core', 'app_config_path'))
                service.saveConfig(data)
            except :
                self.renderJSON({'error':'exception in process data'})
        else:
            self.renderJSON({'error':'cant find data'})

        self.renderJSON({'success':'success'})


    def renderJSON(self, data):
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(data))