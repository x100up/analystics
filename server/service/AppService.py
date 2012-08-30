import json, os, re





class AppService():
    nameR = re.compile('^(.*)\.json$')

    def __init__(self, config_folder):
        self.folder = config_folder

    def getAppConfigList(self):
        '''
        return list of available config apps
        stored in app_config_path
        '''
        return [self.nameR.search(file).group(1) for file in os.listdir(self.folder)]

    def getAppKeyConfig(self, appName):
        return json.load(open(self.folder + '/' + appName + '.json', 'r'))

    def getConfigTags(self, appName, keyName, prefix):
        config = getAppKeyConfig(appName)
        keyConf = config['keys'][keyName]

        raw_json = {}
        if keyConf.has_key(prefix + 'HaveTags'):
            for tag in keyConf[prefix + 'HaveTags']:
                raw_json[tag] = config['tags'][tag]


        if keyConf.has_key(prefix + 'mustHaveSlice'):
            for slice in keyConf[prefix + 'mustHaveSlice']:
                for tag in config['slices'][slice]:
                    raw_json[prefix + 'mustHaveTags'][tag] = config['tags'][tag]

        return raw_json

