import shutil
import os
import sqlite3
import contextlib
import sys

DATABASE_URL = 'file:reg.sqlite?mode=rwc'

def corrupt_database():
    shutil.copy('reg.sqlite', 'regbackup.sqlite')
    os.remove('reg.sqlite')

def restore_database():
    shutil.copy('regbackup.sqlite', 'reg.sqlite')

def drop_classes():
    try:
        with sqlite3.connect(
                DATABASE_URL,
                isolation_level=None,
                uri=True) as connection:

            # drop a table in reg.sqlite
            with contextlib.closing(connection.cursor()) as cursor:
                cursor.execute('DROP TABLE classes')

    except Exception as ex:
        print(f'{sys.argv[0]}: {ex}',
              file = sys.stderr)
        sys.exit(1)
        
def drop_class(class_num):
    try:
        with sqlite3.connect(
                DATABASE_URL,
                isolation_level=None,
                uri=True) as connection:

            # drop a table in reg.sqlite
            with contextlib.closing(connection.cursor()) as cursor:
                cursor.execute('DELETE FROM classes WHERE classes.classid = ' + str(class_num))

    except Exception as ex:
        print(f'{sys.argv[0]}: {ex}',
              file = sys.stderr)
        sys.exit(1)

# drop_class(8321)
restore_database()
