# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

from base import *
import random

import bnw_core.bnw_objects as objs

@require_auth
@defer.inlineCallbacks
def cmd_on(request):
    request.user['off']=False
    _ = yield objs.User.mupdate({'name':request.user['name']},request.user)
    defer.returnValue(
        dict(ok=True,desc='Welcome back!')
    )

@require_auth
@defer.inlineCallbacks
def cmd_off(request):
    request.user['off']=True
    _ = yield objs.User.mupdate({'name':request.user['name']},request.user)
    defer.returnValue(
        dict(ok=True,desc='C u l8r!')
    )
