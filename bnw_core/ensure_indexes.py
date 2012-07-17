#!/usr/bin/env python
from datetime import *

import sys
sys.path.append('..')
import bnw_shell

import time
from twisted.internet import defer, reactor

from bnw_core import base
from bnw_core import bnw_objects as objs

@defer.inlineCallbacks
def index():
    for name in dir(objs):
        cls = getattr(objs,name)
        if isinstance(cls,type):
            if issubclass(cls,objs.MongoObject) and cls!=objs.MongoObject:
                print "---",name
                _ = yield cls.ensure_indexes()
    reactor.stop()
    defer.returnValue(None)

if __name__=="__main__":
    #configfile, dbpath, period = sys.argv[1:]
    import config
    base.config.register(config)
    index()
    reactor.run()
