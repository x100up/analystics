#!/usr/bin/python
import os, sys
from utils.daemon import Daemon
from applications.AnalyticsServer import AnalyticsServer

def startApp(debug = False):
    application = AnalyticsServer(debug)
    application.start()

class ServerDaemon(Daemon):
        def run(self):
            startApp()

def getDaemon():
    log = os.path.abspath("log/log.log")
    return ServerDaemon('/var/run/python-server.pid', stdin=log, stdout=log, stderr=log)

if __name__ == "__main__":

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            getDaemon().start()
        elif 'stop' == sys.argv[1]:
            getDaemon().stop()
        elif 'restart' == sys.argv[1]:
            getDaemon().restart()
        elif 'debug' == sys.argv[1]:
            startApp(True)
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart|debug" % sys.argv[0]
        sys.exit(2)