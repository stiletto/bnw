# -*- coding: utf-8 -*-

from base import *
import random
import time
from bnw.core.base import BnwResponse, config
import bnw.core.bnw_objects as objs

@defer.inlineCallbacks
def throttle_check(user):
    throttle = yield objs.Throttle.find_and_modify({'user': user},{'$inc':{'bucket':1}},upsert=True)
    if throttle and throttle.get('bucket',0) >= config.throttle_bucket_size:
        raise BnwResponse('You are sending messages too fast! Please wait %d seconds before trying again.' % (throttle['bucket']*config.throttle_leak,))
    defer.returnValue(throttle)

@defer.inlineCallbacks
def throttle_leak():
    yield objs.Throttle.mupdate({'bucket':{'$gt':0}}, {'$inc':{'bucket':-1}}, multi=True)
    reactor.callLater(config.throttle_leak_speed, throttle_leak)
    defer.returnValue(None)

def setup_throttle():
    if config.throttle_leak_speed > 0:
        reactor.callLater(config.throttle_leak_speed, throttle_leak)
