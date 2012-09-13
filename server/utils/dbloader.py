import os
import codecs
from state import State

def migrate(connection = None):
    dirList = os.listdir('sql')
    files = []
    for fname in dirList:
        index, name = fname.split('-', 1)
        files.append((int(index), name))

    # sort by index
    files = sorted(files)

    state = State()
    currentDBVersion = state.get('currentDBVersion')

    for index, name in files:
        if index > currentDBVersion:
            filename = str(index) + '-' + name

            file = codecs.open('sql/' + filename, "r", "utf-8-sig")
            connection.flush()
            sql = file.read()
            connection.execute(sql)

            currentDBVersion = index
            state.set('currentDBVersion', currentDBVersion)
