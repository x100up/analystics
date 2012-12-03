# coding=utf-8

from AdminIndexController import AdminAction
from models.Spell import Spell
from services.AppService import AppService
from services.SpellService import SpellService

class IndexAction(AdminAction):

    def _prepare(self, appCode):
        appService = AppService(self.application.getAppConfigPath())
        self.appconfig = appService.getAppConfig(appCode=appCode)
        self.spell = Spell()
        self.spellService = SpellService(self.application.spellFolder, appCode)

    def get(self, *args, **kwargs):
        app = self.checkAppAccess(args)
        self._prepare(app.code)
        print self.spellService.get('key', 'coins_spend_event_key', 'legend_name')
        self._render()

    def post(self, *args, **kwargs):
        app = self.checkAppAccess(args)
        self._prepare(app.code)
        data = {'key':{}, 'tag':{}}
        
        for eventCode in self.appconfig['keys']:
            for spellKey in self.spell.keyFields:
                val = self.get_argument('spellKey|{}|{}'.format(spellKey, eventCode), default=None)
                if val:
                    if not data['key'].has_key(eventCode):
                        data['key'][eventCode] = {}

                    data['key'][eventCode][spellKey] = val


        for tagCode in self.appconfig['tags']:
            for spellKey in self.spell.tagFields:
                val = self.get_argument('spellTag|{}|{}'.format(spellKey, tagCode), default=None)
                if val:
                    if not data['tag'].has_key(tagCode):
                        data['tag'][tagCode] = {}

                    data['tag'][tagCode][spellKey] = val

        self.spellService.save(data)
        self._render()

    def _render(self):
        self.render('admin/spell/index.jinja2', {'spell':self.spell, 'appconfig':self.appconfig, 'spellService':self.spellService})