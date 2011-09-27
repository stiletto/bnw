# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

from base import *
import random

import bnw_core.bnw_objects as objs

optionnames = [ 'usercss', 'password' ]
@require_auth
@defer.inlineCallbacks
def cmd_set(request,**kwargs):
    """ Настройки """
    if not kwargs:
        current = request.user.get('settings',{})
        defer.returnValue(
            dict(ok=True,format='settings',settings=current)
        )
    else:
        for n in optionnames:
            if n in kwargs:
                v = kwargs[n]
                if len(v)>2048:
                    defer.returnValue(
                        dict(ok=False,desc='%s is too long.' % (n,))
                    )
                _ = yield objs.User.mupdate({'name':request.user['name']},
                    {'$set':{'settings.'+n:v}},safe=True)
        defer.returnValue(
            dict(ok=True,desc='Settings updated.')
        )
