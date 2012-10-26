# coding=utf-8
from AdminIndexController import AdminAction
from services.AppService import AppService
from components.AnalyticsException import AnalyticsException
from pprint import pprint
class TagEditAction(AdminAction):
    def prepare(self):
        super(TagEditAction, self).prepare()
        self.errors = []
        self.appService = AppService(self.application.getAppConfigPath())

    def post(self, *args, **kwargs):
        app_code, = args

        tag_indexes = self.get_arguments('tag_index')

        tag_conf = {}
        for tag_index in tag_indexes:
            tag_code = self.get_argument('tag_{}_code'.format(tag_index), False)
            if not tag_code:
                continue

            tag_conf[tag_code] = {}
            tag_conf[tag_code]['type'] = self.get_argument("tag_{}_type".format(tag_index))
            tag_conf[tag_code]['name'] = self.get_argument("tag_{}_name".format(tag_index), default='')
            if tag_conf[tag_code]['type'] == 'choose':
                count = int(self.get_argument('tag_{}_values_count'.format(tag_index), default=0))
                values = {}
                isDict = False

                for index in range(0, count + 1):
                    key = self.get_argument('tag_{}_values_key_{}'.format(tag_index, index), default=None)
                    value = self.get_argument('tag_{}_values_value_{}'.format(tag_index, index), default=None)
                    if key is None:
                        continue
                    if not isDict:
                        isDict = not value is None
                    values[key] = value

                if not isDict:
                    values = values.keys()

                if not len(values):
                    self.errors.append(u'Для типа выбора (тег {0}) должен быть хотя бы один вариант'.format(tag_code))

                tag_conf[tag_code]['values'] = values


        key_conf = {}
        key_indexes = self.get_arguments('key_index')
        if key_indexes:
            key_conf = {}
            for index in key_indexes:
                key_name = self.get_argument('key_{}_name'.format(index), False)
                if key_name:
                    key_conf[key_name] = {}
                    desc = self.get_argument('key_{}_desc'.format(index), False)
                    if desc:
                        key_conf[key_name]['description'] = desc

                tag_indexes = self.get_arguments('have_key_tag_' + index)
                if tag_indexes:
                    for tag_index in tag_indexes:
                        tag_code = self.get_argument('tag_{}_code'.format(tag_index), False)
                        if tag_code and tag_conf.has_key(tag_code):
                            if not key_conf[key_name].has_key('mustHaveTags'):
                                key_conf[key_name]['mustHaveTags'] = []
                            key_conf[key_name]['mustHaveTags'].append(tag_code)

        if not self.errors:
            self.appService.saveSettings(app_code, tagSettings=tag_conf, keyConfig=key_conf)

        self.run(tag_conf, key_conf)


    def showTags(self, app_code):
        tags = {}
        try:
            raw_tags = self.appService.getTagList(app_code)
            settings = self.appService.getTagSettings(app_code)
            for tag in raw_tags:
                tags[tag] = {}
                if settings.has_key(tag):
                    tags[tag] = settings[tag]
        except AnalyticsException as analyticsException:
            self.errors.append(analyticsException.message)

        keys = {}
        try:
            keys = self.appService.getKeys(app_code)
        except AnalyticsException as analyticsException:
            self.errors.append(analyticsException.message)



        self.run(tags, keys)

    def get(self, *args, **kwargs):
        app_code, = args

        if not self.appService.isConfigExist(app_code):
            self.appService.createEmptyConfig(app_code)

        self.showTags(app_code)


    def run(self, tags, keys):
        dict = {'tags': tags, 'keys': keys}
        dict['errors'] = self.errors

        relation_cache = {}
        tag_indexes = {}
        i=0
        for tag_name, tag_data in tags.items():
            tag_indexes[tag_name] = str(i)
            i += 1

        for index, key_code in enumerate(keys):
            relation_cache[index] = []
            key_data = keys[key_code]
            if key_data.has_key('mustHaveTags'):
                for tag_name in key_data['mustHaveTags']:
                    relation_cache[index].append(tag_indexes[tag_name])

        dict['js_vars'] = {'relation_cache': relation_cache}
        self.render('admin/editTags.jinja2', dict)