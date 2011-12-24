from twisted.internet import defer

import txmongo
from txmongo import gridfs
from txmongo.collection import errors as mongo_errors

from base import config


connection=None
db=None


@defer.inlineCallbacks
def get_connection():
    global connection
    if connection is None:
        connection = (yield txmongo.MongoConnection())
    defer.returnValue(connection)
    
@defer.inlineCallbacks
def get_db(collection=None):
    global db
    if not db:
        db=(yield get_connection())[config.database]
    if collection is None:
        defer.returnValue(db)
    else:
        defer.returnValue(db[collection])

def get_db_existing(collection=None):
    global db
    if db is None:
        return db
    else:
        return db[collection]

@defer.inlineCallbacks
def get_fs(collection="fs"):
    db = (yield get_connection())[config.database_fs]
    fs = gridfs.GridFS(db,collection=collection)
    defer.returnValue(fs)

def gc(key):
    global config
    return getattr(config,key)
