# coding: utf-8

from tornado.concurrent import Future
from twisted.internet import defer
import motor

from bnw_mongo import get_db
from bnw_objects import fudef

fss = {}

class BnwGridException(Exception): pass

def get_fs(collection):
    global fss
    d = defer.Deferred()
    fs = fss.get(collection)
    if fs:
        return fs
    raise BnwGridException('GridFS is not ready yet')



def open_gridfs():
    for collection in ('avatars',):
        def set_fs(fs, error):
            if error: raise error
            global fss
            fss[collection] = GridFSWrapper(fs, collection)
        motor.MotorGridFS(get_db(), collection=collection).open(set_fs)

class GridFSWrapper(object):
    def __init__(self, collection, collection_name):
        self.collection = collection_name
        self.collection_name = collection_name

    def __getattr__(self, db_method):
        method = getattr(self.collection, db_method)
        def fn(*args, **kwargs):
            print 'grid method',db_method,args,kwargs
            f = method(*args, **kwargs)
            if isinstance(f, Future):
                return fudef(f)
            return f
        return fn
