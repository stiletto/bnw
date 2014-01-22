from twisted.internet import defer

#import txmongo
#from txmongo import gridfs
#from txmongo.collection import errors as mongo_errors
from tornado.ioloop import IOLoop
import motor
from pymongo.read_preferences import ReadPreference

from base import config


connection = None
db = None
fs = None
fs_avatars = None

def open_db():
    global db, fs
    client = motor.MotorReplicaSetClient(config.database_uri,read_preference=ReadPreference.NEAREST, replicaSet='shiplica')
    IOLoop.current().run_sync(client.open)
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

