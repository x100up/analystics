__author__ = 'x100up'

from optparse import OptionParser

optParser = OptionParser()
optParser.add_option("-a", "--app", dest="appname", help="application name")
optParser.add_option("-x", "--all", dest="all_apps", help="all applications", action="store_true")

(options, args) = optParser.parse_args()
scriptName = args[0]
options = options.__dict__

if scriptName == 'initHiveMeta':
    from scripts.initHiveMetaData import InitHiveMetaDataScript
    script = InitHiveMetaDataScript(options)
    script.run()

