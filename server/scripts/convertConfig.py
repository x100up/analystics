# -*- coding: utf-8 -*-
from scripts.baseScript import BaseAnalyticsScript

class ConvertConfig(BaseAnalyticsScript):

    def run(self):
        config = self.appService.getRawAppConfig('topface')

        bunchTags = []
        for bunch in config['bunches']:
            bunchTags =  bunchTags + bunch['tags']

        tagCounter = {}
        for key in config['keys']:
            if key['tags']:
                for tagCode in key['tags']:
                    if not tagCode in tagCounter:
                        tagCounter[tagCode] = []
                    tagCounter[tagCode].append(key['code'])

        newTags = []
        for tag in config['tags']:
            tagCode = tag['code']
            if tagCode in bunchTags:
                newTags.append(self.getTag(config, tagCode))
                #print 'Tag {} in bunch'.format(tagCode)
                continue

            if tagCounter.has_key(tagCode) and not len(tagCounter[tagCode]) == 1:
                newTags.append(self.getTag(config, tagCode))
                #print 'Tag {} more then once {}'.format(tagCode, tagCounter[tagCode])
                continue

            if tagCounter.has_key(tagCode):
                keyCode = tagCounter[tagCode][0]
                for i, key in enumerate(config['keys']):
                    if key['code'] == keyCode:
                        key['tags'][tagCode] = self.getTag(config, tagCode)
                        break


        config['tags'] = newTags
        self.appService.saveConfig(config)



    def getTag(self, conf, tagCode):
        for tag in conf['tags']:
            if tag['code'] == tagCode:
                return tag