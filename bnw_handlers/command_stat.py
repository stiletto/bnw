# -*- coding: utf-8 -*-

import time
from base import *
from twisted.internet import defer
import bnw_core.bnw_objects as objs

@defer.inlineCallbacks
def cmd_stat(request):
    messages = list(x.doc for x in (yield objs.StatMessages.find({},limit=500)))
    comments = list(x.doc for x in (yield objs.StatComments.find({},limit=500)))
    defer.returnValue(dict(ok=True,desc='Oh, hai!',messages=messages,comments=comments,cache=3600,cache_public=True))
