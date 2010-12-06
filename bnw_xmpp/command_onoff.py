# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

from base import *
import random

import bnw_core.bnw_objects as objs

@require_auth
@defer.inlineCallbacks
def cmd_on(request):
    msg.user['off']=False
    _ = yield objs.User.mupdate({'name':msg.user['name']},msg.user)
    defer.returnValue(
        dict(ok=True,desc='Welcome back!')
    )

@require_auth
@defer.inlineCallbacks
def cmd_off(request):
    msg.user['off']=True
    _ = yield objs.User.mupdate({'name':msg.user['name']},msg.user)
    defer.returnValue(
        dict(ok=True,desc='C u l8r!')
    )
