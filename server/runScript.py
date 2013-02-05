#!/usr/bin/python
__author__ = 'x100up'

from optparse import OptionParser

optParser = OptionParser()
optParser.add_option("-a", "--app", dest="appname", help="application name")
optParser.add_option("-x", "--all", dest="all_apps", help="all applications", action="store_true")
optParser.add_option("-y", "--year", dest="year", help="year")
optParser.add_option("-m", "--month", dest="month", help="month")
optParser.add_option("-d", "--day", dest="day", help="day")
optParser.add_option("-e", "--event", dest="event", help="event")
optParser.add_option("-s", "--skipCheckInDB", dest="skipCheckInDB", help="event", type=bool)

scripts = ['initHiveMeta', 'packer', 'monitor', 'convertConfig']

(options, args) = optParser.parse_args()
if not len(args) == 1 or not args[0]  in scripts:
    print 'You must specified script {}'.format(str(scripts))
    exit()


scriptName = args[0]
options = options.__dict__

if scriptName == 'initHiveMeta':
    from scripts.initHiveMetaData import InitHiveMetaDataScript
    script = InitHiveMetaDataScript(options)
    script.run()

if scriptName == 'packer':
    from scripts.packer import PackerScript
    script = PackerScript(options)
    script.run()


if scriptName == 'monitor':
    from scripts.monitor import MonitorScript
    script = MonitorScript(options)
    script.run()

if scriptName == 'updateDB':
    from scripts.updateDB import UpdateDbScript
    script = UpdateDbScript(options)
    script.run()

if scriptName == 'convertConfig':
    from scripts.convertConfig import ConvertConfig
    script = ConvertConfig(options)
    script.run()
