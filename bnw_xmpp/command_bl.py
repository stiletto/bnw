# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

from base import *
import random

import bnw_core.bnw_objects as objs

optionnames = [ 'usercss', 'password' ]

@defer.inlineCallbacks
def bl_internal(user,what,delete,text):
    action = '$pull' if delete else '$addToSet'
    defer.returnValue((yield objs.User.mupdate({'name':user},{action: { 'blacklist': [what,text]}},safe=True)))

@require_auth
@defer.inlineCallbacks
def cmd_blacklist(request,user="",tag="",club="",delete=""):
    """ Черный список """
    if not delete and len(request.user.get('blacklist',[]))>2048:
        defer.returnValue(
            dict(ok=False,desc='Stop being a blacklist-faggot.')
        )
    if (user and tag) or (user and club) or (tag and club):
        defer.returnValue(
            dict(ok=False,desc='Complex subscriptions and blacklist aren''t supported.')
        )

    if user:
        _ = yield bl_internal(request.user['name'],'user',delete,user[:128])
    elif tag:
        _ = yield bl_internal(request.user['name'],'tag',delete,tag[:256])
    elif club:
        _ = yield bl_internal(request.user['name'],'club',delete,club[:256])
    else:
        defer.returnValue(
            dict(ok=True, format="blacklist",
                blacklist=request.user.get('blacklist',[]))
        )
    defer.returnValue(
            dict(ok=True,desc='Blacklist updated.')
        )
