__author__ = 'prog-31'

import threading

def getAliveThreads():
        threadList = threading.enumerate()
        threadNames = []
        for thread in threadList:
            threadNames.append(thread.getName())
        return threadNames
