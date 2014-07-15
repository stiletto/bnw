import logging
import pymongo
from pymongo.read_preferences import ReadPreference

from bnw.core.config import config


connection = None
db = None
fs = None
fs_avatars = None

def open_db(uri, rs, database, database_fs):
    if rs:
        client = pymongo.MongoReplicaSetClient(uri, read_preference=ReadPreference.NEAREST, replicaSet=rs)
    else:
        client = pymongo.MongoClient(uri)
    db = client[database]
    fs = client[database_fs]
    return db, fs

#def get_fs(collection="fs"):
#    return motor.MotorGridFS(fs, collection)

def gc(key):
    global config
    return getattr(config, key)

def _config_update_handler(old, new):
    if old.compare(new, 'database_uri', 'database_rs', 'database', 'database_fs'): return

    try:
        new_db, new_fs = open_db(new['database_uri'], new['database_rs'], new['database'], new['database_fs'])
    except Exception as e:
        logging.error('Unable to create database connection: %s' % (e,))
        raise
    global db, fs
    db = new_db
    fs = new_fs
    return

config.register_handler(_config_update_handler)
