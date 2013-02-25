# -*- coding: utf-8 -*-
# from twisted.words.xish import domish

from base import *
import random

import bnw_core.bnw_objects as objs


@require_auth
@defer.inlineCallbacks
def cmd_on(request):
    """ Включение доставки сообщений """
    _ = yield objs.User.mupdate({'name': request.user['name']}, {'$set': {'off': False}}, safe=True)
    if request.user.get('off', False):
        defer.returnValue(
            dict(ok=True, desc='Welcome back!')
        )
    else:
        defer.returnValue(
            dict(ok=True, desc='Welcoooome baaaack, I said.')
        )


@require_auth
@defer.inlineCallbacks
def cmd_off(request):
    """ Выключение доставки сообщений """
    _ = yield objs.User.mupdate({'name': request.user['name']}, {'$set': {'off': True}}, safe=True)
    if request.user.get('off', False):
        defer.returnValue(
            dict(ok=True, desc='See you later.')
        )
    else:
        defer.returnValue(
            dict(ok=True, desc='C u l8r!')
        )
