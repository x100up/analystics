#!/usr/bin/python
__author__ = 'x100up'

from optparse import OptionParser

optParser = OptionParser()
optParser.add_option("-a", "--app", dest="appname", help="application name")
optParser.add_option("-x", "--all", dest="all_apps", help="all applications", action="store_true")
optParser.add_option("-y", "--year", dest="year", help="year")
optParser.add_option("-m", "--month", dest="month", help="month")
optParser.add_option("-d", "--day", dest="day", help="day")

(options, args) = optParser.parse_args()
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
