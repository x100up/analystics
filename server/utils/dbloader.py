import inspect
import os
import codecs
from state import State

def migrate(connection = None):
    thisPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    sqlPath = os.path.abspath(thisPath + '/../../sql/')

    dirList = os.listdir(sqlPath)
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

            file = codecs.open(sqlPath + '/' + filename, "r", "utf-8-sig")
            if hasattr(connection, 'flush'):
                connection.flush()
            sql = file.read()
            connection.execute(sql)

            currentDBVersion = index
            state.set('currentDBVersion', currentDBVersion)
