import shutil
import os

def corrupt_database():
    shutil.copy('reg.sqlite', 'regbackup.sqlite')
    os.remove('reg.sqlite')

def restore_database():
    shutil.copy('regbackup.sqlite', 'reg.sqlite')

restore_database()
