# -*- coding: utf-8 -*-
import random
from twisted.internet import defer

from delayed_global import DelayedGlobal

idchars='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    
def genid(idlen):
    return ''.join(random.choice(idchars) for i in xrange(0,idlen))
    
def cropstring(string,maxlen):
    return string if len(string)<=maxlen else string[:maxlen]+u'...'
        
def _(s,user):
    return s
    
config=DelayedGlobal('config')
            
import txmongo
from txmongo import gridfs
from txmongo.collection import errors as mongo_errors
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
        db=(yield get_connection()).bnw
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
    db = (yield get_connection()).bnw_fs
    fs = gridfs.GridFS(db,collection=collection)
    defer.returnValue(fs)

def gc(key):
    global config
    return getattr(config,key)

class BnwResponse(Exception): # we do it idiotic way!
    pass
