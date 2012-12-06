class TagGroup():
    def __init__(self, data = None):
        self.index = None
        self.name = None
        if data:
            self.createFromDict(data)

    def createFromDict(self, data):
        if data.has_key('name'):
            self.name = data['name']

        if data.has_key('index'):
            self.index = int(data['index'])

    def toObject(self):
        return {
            'name': self.name,
            'index': self.index,
        }