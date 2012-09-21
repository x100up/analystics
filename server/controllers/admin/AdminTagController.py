# coding=utf-8
from AdminIndexController import AdminAction
from services.AppService import AppService

class TagEditAction(AdminAction):
    def prepare(self):
        self.errors = []
        self.appService = AppService(self.application.getAppConfigPath())

    def post(self, *args, **kwargs):
        app_code, = args
        tags = self.get_arguments('tags')

        conf = {}
        for tag in tags:
            conf[tag] = {}
            conf[tag]['type'] = self.get_argument(tag + "_type")
            conf[tag]['name'] = self.get_argument(tag + "_name", default='')
            if conf[tag]['type'] == 'choose':
                count = int(self.get_argument(tag + '_values_count', default=0))
                values = {}
                isDict = False
                for index in range(1, count + 1):
                    key = self.get_argument(tag + '_values_key_' + str(index), default=None)
                    value = self.get_argument(tag + '_values_value_' + str(index), default=None)
                    if key is None:
                        continue
                    isDict = not value is None
                    values[key] = value

                if not isDict:
                    values = values.keys()

                if not len(values):
                    self.errors.append(u'Для типа выбора (тег {0}) должен быть хотя бы один вариант'.format(tag))

                conf[tag]['values'] = values

        if not self.errors:
            self.appService.saveTagSettings(app_code, conf)

        self.run({'tags': conf})


    def showTags(self, app_code):
        tags = self.appService.getTagList(app_code)
        settings = self.appService.getTagSettings(app_code)
        data = {}
        for tag in tags:
            data[tag] = {}
            if settings.has_key(tag):
                data[tag] = settings[tag]

        self.run({'tags': data})

    def get(self, *args, **kwargs):
        app_code, = args
        self.showTags(app_code)


    def run(self, dict=None):
        if dict is None:
            dict = {}
        dict['errors'] = self.errors
        self.render('admin/editTags.jinja2', dict)