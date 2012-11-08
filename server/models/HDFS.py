# coding=utf-8
__author__ = 'pavlenko.roman.spb@gmail.com'


class HDFS_item(object):

    def __init__(self):
        self.dir = None
        self.accessTime = None
        self.blockSize = None
        self.group = None
        self.length = None
        self.modificationTime = None
        self.owner = None
        self.pathSuffix = None
        self.permission = None
        self.replication = None
        self.type = None

    def toObj(self):
        return self.__dict__


    @staticmethod
    def create(values):
        item = HDFS_item()
        for k, v in values.items():
            if hasattr(item, k):
                item.__setattr__(k, v)

        return item

