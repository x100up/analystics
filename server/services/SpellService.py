# coding=utf-8
__author__ = 'pavlenko.roman.spb@gmail.com'
import os, json

class SpellService():
    def __init__(self, folder, appCode):
        self.folder = folder
        self.appCode = appCode
        self.spellData = {}
        self.load()


    def load(self):
        path = self.folder + self.appCode + '.json'
        if os.path.exists(path):
            p = open(path, 'r')
            self.spellData = json.load(p)
            p.close()


    def get(self, group, index, key):
        if self.spellData.has_key(group):
            if self.spellData[group].has_key(index):
                if self.spellData[group][index].has_key(key):
                    return self.spellData[group][index][key]
        return None

    def save(self, data):
        path = self.folder + self.appCode + '.json'
        p = open(path, 'w')
        json.dump(data, p)
        p.close()
        self.spellData = data
