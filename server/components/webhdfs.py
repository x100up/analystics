import httplib
import urlparse
import json
import logging

logging.basicConfig(level=logging.ERROR, datefmt='%m/%d/%Y %I:%M:%S %p',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(name='webhdfs')

WEBHDFS_CONTEXT_ROOT="/webhdfs/v1"

class WebHDFS(object):

    def __init__(self, namenode_host, namenode_port, hdfs_username):
        self.namenode_host=namenode_host
        self.namenode_port = namenode_port
        self.username = hdfs_username

    def debug(self, message):
        #print '     --hdfs-->' + message
        pass


    def mkdir(self, path):
        url_path = WEBHDFS_CONTEXT_ROOT + path +'?op=MKDIRS&user.name='+self.username
        self.debug("Create directory: " + url_path)
        httpClient = self.__getNameNodeHTTPClient()
        httpClient.request('PUT', url_path , headers={})
        response = httpClient.getresponse()
        self.debug("HTTP Response: %d, %s"%(response.status, response.reason))
        httpClient.close()


    def rmdir(self, path):
        url_path = WEBHDFS_CONTEXT_ROOT + path +'?op=DELETE&recursive=true&user.name='+self.username
        self.debug("Delete directory: " + url_path)
        httpClient = self.__getNameNodeHTTPClient()
        httpClient.request('DELETE', url_path , headers={})
        response = httpClient.getresponse()
        self.debug("HTTP Response: %d, %s"%(response.status, response.reason))
        httpClient.close()


    def copyFromLocal(self, source_path, target_path, replication=1):
        url_path = WEBHDFS_CONTEXT_ROOT + "/" + target_path + '?op=CREATE&overwrite=true&user.name='+self.username

        httpClient = self.__getNameNodeHTTPClient()
        httpClient.request('PUT', url_path , headers={})
        response = httpClient.getresponse()
        self.debug("HTTP Response: %d, %s"%(response.status, response.reason))
        msg = response.msg
        redirect_location = msg["location"]
        self.debug("HTTP Location: %s"%(redirect_location))
        result = urlparse.urlparse(redirect_location)
        redirect_host = result.netloc[:result.netloc.index(":")]
        redirect_port = result.netloc[(result.netloc.index(":")+1):]
        # Bug in WebHDFS 0.20.205 => requires param otherwise a NullPointerException is thrown
        redirect_path = result.path + "?" + result.query + "&replication="+str(replication)

        self.debug("Send redirect to: host: %s, port: %s, path: %s "%(redirect_host, redirect_port, redirect_path))
        fileUploadClient = httplib.HTTPConnection(redirect_host,
            redirect_port, timeout=600)
        # This requires currently Python 2.6 or higher
        fileUploadClient.request('PUT', redirect_path, open(source_path, "r").read(), headers={})
        response = fileUploadClient.getresponse()
        self.debug("HTTP Response: %d, %s"%(response.status, response.reason))
        httpClient.close()
        fileUploadClient.close()
        return response.status


    def copyToLocal(self, source_path, target_path):
        url_path = WEBHDFS_CONTEXT_ROOT + "/" + source_path+'?op=OPEN&overwrite=true&user.name='+self.username
        self.debug("GET URL: %s"%url_path)
        httpClient = self.__getNameNodeHTTPClient()
        httpClient.request('GET', url_path , headers={})
        response = httpClient.getresponse()
        # if file is empty GET returns a response with length == NONE and
        # no msg["location"]
        if response.length!=None:
            msg = response.msg
            redirect_location = msg["location"]
            self.debug("HTTP Response: %d, %s"%(response.status, response.reason))
            self.debug("HTTP Location: %s"%(redirect_location))
            result = urlparse.urlparse(redirect_location)
            redirect_host = result.netloc[:result.netloc.index(":")]
            redirect_port = result.netloc[(result.netloc.index(":")+1):]

            redirect_path = result.path + "?" + result.query

            self.debug("Send redirect to: host: %s, port: %s, path: %s "%(redirect_host, redirect_port, redirect_path))
            fileDownloadClient = httplib.HTTPConnection(redirect_host,
                redirect_port, timeout=600)

            fileDownloadClient.request('GET', redirect_path, headers={})
            response = fileDownloadClient.getresponse()
            self.debug("HTTP Response: %d, %s"%(response.status, response.reason))

            # Write data to file
            target_file = open(target_path, "w")
            target_file.write(response.read())
            target_file.close()
            fileDownloadClient.close()
        else:
            target_file = open(target_path, "w")
            target_file.close()

        httpClient.close()
        return response.status


    def listdir(self, path):
        url_path = WEBHDFS_CONTEXT_ROOT + path + '?op=LISTSTATUS&user.name=' + self.username
        self.debug("List directory: " + url_path)
        httpClient = self.__getNameNodeHTTPClient()
        httpClient.request('GET', url_path , headers={})
        response = httpClient.getresponse()
        self.debug("HTTP Response: %d, %s"%(response.status, response.reason))
        data_dict = json.loads(response.read())
        self.debug("Data: " + str(data_dict))
        files = []

        if data_dict.has_key('RemoteException'):
            raise WebHDFSException(data_dict['RemoteException']['message'], data_dict['RemoteException']['exception'])

        for i in data_dict["FileStatuses"]["FileStatus"]:
            self.debug(i["type"] + ": " + i["pathSuffix"])
            files.append(i["pathSuffix"])
        httpClient.close()
        return files

    def list(self, path):
        url_path = WEBHDFS_CONTEXT_ROOT + path + '?op=LISTSTATUS&user.name=' + self.username
        httpClient = self.__getNameNodeHTTPClient()
        httpClient.request('GET', url_path , headers={})
        response = httpClient.getresponse()
        data_dict = json.loads(response.read())
        if data_dict.has_key('RemoteException'):
            raise WebHDFSException(data_dict['RemoteException']['message'], data_dict['RemoteException']['exception'])
        return data_dict['FileStatuses']['FileStatus']

    def dirSummary(self, path):
        url_path = WEBHDFS_CONTEXT_ROOT + path + '?op=GETCONTENTSUMMARY&user.name=' + self.username
        httpClient = self.__getNameNodeHTTPClient()
        httpClient.request('GET', url_path , headers={})
        response = httpClient.getresponse()
        data_dict = json.loads(response.read())
        if data_dict.has_key('RemoteException'):
            raise WebHDFSException(data_dict['RemoteException']['message'], data_dict['RemoteException']['exception'])
        return data_dict['ContentSummary']


    def status(self, path):
        url_path = WEBHDFS_CONTEXT_ROOT +path+'?op=GETFILESTATUS&user.name='+self.username
        self.debug("Get file status: " + url_path)
        httpClient = self.__getNameNodeHTTPClient()
        httpClient.request('GET', url_path , headers={})
        response = httpClient.getresponse()
        self.debug("HTTP Response: %d, %s"%(response.status, response.reason))
        data_dict = json.loads(response.read())
        if data_dict.has_key('RemoteException'):
            raise Exception(data_dict['RemoteException']['message'])

        self.debug("Data: " + str(data_dict))
        files=[]
        for i in data_dict["FileStatuses"]["FileStatus"]:
            self.debug(i["type"] + ": " + i["pathSuffix"])
            files.append(i["pathSuffix"])
        httpClient.close()
        return files

    def __getNameNodeHTTPClient(self):
        httpClient = httplib.HTTPConnection(self.namenode_host,
            self.namenode_port,
            timeout=600)
        return httpClient

class WebHDFSException(BaseException):

    FileNotFoundException = 'FileNotFoundException'

    def __init__(self, message, name):
        super(WebHDFSException, self).__init__()
        self.message = message
        self.name = name

from datetime import date

class AnalyticsWebHDFS():

    def __init__(self, namenode_host, namenode_port, hdfs_username, stat_root):
        self.webHDFSClient = WebHDFS(namenode_host, namenode_port, hdfs_username)
        self.stat_root = stat_root

    def getEventCodes(self, appCode):
        return self.webHDFSClient.listdir(self.stat_root + appCode)

    def getPartitions(self, appCode, eventCode):
        partitions = []
        folder = self.stat_root + appCode + '/' + eventCode
        years = self.webHDFSClient.listdir(folder)
        for year in years:
            months = self.webHDFSClient.listdir(folder + '/' + year)
            for month in months:
                days = self.webHDFSClient.listdir(folder + '/' + year + '/' + month)
                for day in days:
                    partitions.append(date(int(year), int(month), int(day)))

        return partitions

    def isPartitionExist(self, appCode, eventCode, date):
        folder = '{}{}/{}/{}/{}/{}/'.format(self.stat_root, appCode, eventCode, date.year, date.month, date.day)
        try:
            data = self.webHDFSClient.listdir(folder)
        except:
            return False
        print bool(data), data
        return bool(data)