import json

def getAppKeyConfig(appName):
    f = open('app_configs/' + appName + '.json', 'r')
    return json.load(f)

def getConfigTags(config, keyName, prefix):
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