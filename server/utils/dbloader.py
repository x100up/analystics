import os
import codecs
from state import State

def migrate(mysql_user = None, mysql_password = None, mysql_dbname = None, connection = None):
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

            if connection:
                file = codecs.open('sql/' + filename, "r", "utf-8-sig")
                connection.flush()
                sql = file.read()
                connection.execute(sql)
            else:
                # run script
                command = 'mysql -u{0} -p{1} {2} < {3}'.format(mysql_user, mysql_password, mysql_dbname, 'sql/' + filename)
                os.system(command)

            currentDBVersion = index
            state.set('currentDBVersion', currentDBVersion)
