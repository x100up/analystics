# -*- coding: utf-8 -*-
import argparse, json, random


print """------------------------------------------------
Application keys, tags, slice config generator
------------------------------------------------"""

parser = argparse.ArgumentParser()
parser.add_argument("appname")

parser.add_argument("--key_prefix","-k",  help="Key name prefix", default="KEY_")
parser.add_argument("--key_count","-c",  help="Key count", default=10)

parser.add_argument("--tag_prefix","-t",  help="Tag prefix", default="TAG_")
parser.add_argument("--tag_count","-g",  help="Tag count", default=20)

parser.add_argument("--slice_prefix","-s",  help="Slice prefix", default="SLICE_")
parser.add_argument("--slice_count","-u",  help="Slice count", default=5)


args = parser.parse_args()

args = vars(args)

## generate

conf = {
    "appname" : args['appname'],
    "keys" : {},
    "tags" : {},
    "slices" : {}
}

def getRandDict(dict, count):
    if len(dict) <= count:
        return dict
    else:
        new_dict = {}
        while len(new_dict) < count:
            key = random.choice(dict.keys())
            if key not in new_dict:
                new_dict[key] = dict[key]
        return new_dict

for tag_index in range(1, args['tag_count'] + 1):
    tag_name = args['tag_prefix'] + str(tag_index)
    conf["tags"][tag_name] = {
        "description": "Tag " + tag_name
    }


for slice_index in range(1, args['slice_count'] + 1):
    slice = []
    for c in range(1, random.randint(2, 5)):
        slice.append(random.choice(conf["tags"].keys()))

    conf["slices"][ args['slice_prefix'] + str(slice_index)] = slice


for key_index in range(1, args['key_count'] + 1):
    key_name = args['key_prefix'] + str(key_index)
    key_data = {"description":"key " + key_name}

    key_data['mustHaveTags'] = getRandDict(conf["tags"], 2).keys()
    key_data['canHaveTags'] = getRandDict(conf["tags"], 2).keys()

    key_data['mustHaveSlice'] = getRandDict(conf["slices"], 2).keys()
    key_data['canHaveSlice'] = getRandDict(conf["slices"], 2).keys()

    conf["keys"][key_name] = key_data


f = open('../app_configs/' + args['appname'] + '.json', 'w')
f.write(json.dumps(conf, indent = True))
f.close()
