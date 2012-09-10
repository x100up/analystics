import json

class State():
    '''
    Define the app state
    '''

    def __init__(self):
        self.file = 'state.json'

    def get(self, varName):
        self.readData()
        if  self.data.has_key(varName):
            return self.data[varName]
        else:
            return None

    def set(self, varName, value):
        self.readData()
        self.data[varName] = value
        self.writeData()


    def readData(self):
        try:
            self.data = json.load(open(self.file, 'r+'))
        except:
            self.data = {}

    def writeData(self):
        json.dump(self.data, open(self.file, 'w+'))
