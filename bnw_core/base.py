# -*- coding: utf-8 -*-
import random,time
from twisted.internet import interfaces, defer, reactor

idchars='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    
def genid(idlen):
    return ''.join(random.choice(idchars) for i in xrange(0,idlen))
    
def cropstring(string,maxlen):
    return string if len(string)<=maxlen else string[:maxlen]+u'...'
        
def _(s,user):
    return s
            
import txmongo
connection=None
@defer.inlineCallbacks
def get_db(collection=None):
    global connection
    if connection is None:
        connection = (yield txmongo.MongoConnection()).bnw
    if collection is None:
        defer.returnValue(connection)
    else:
        defer.returnValue(connection[collection])

def get_db_existing(collection=None):
    global connection
    if collection is None:
        return connection
    else:
        return connection[collection]
