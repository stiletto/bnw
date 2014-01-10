import pymongo
from pymongo.read_preferences import ReadPreference

from bnw.core.config import config


connection = None
db = None
fs = None
fs_avatars = None

def open_db():
    global db, fs
    client = pymongo.MongoReplicaSetClient(config.database_uri, read_preference=ReadPreference.NEAREST, replicaSet=config.database_rs or None)
    db = client[config.database]
    fs = client[config.database_fs]

def get_db(collection=None):
    global db
    if collection is None:
        return db
    return db[collection]

#def get_fs(collection="fs"):
#    return motor.MotorGridFS(fs, collection)

def gc(key):
    global config
    return getattr(config, key)

