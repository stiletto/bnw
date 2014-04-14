# -*- coding: utf-8 -*-
# from twisted.words.xish import domish

from base import *
import random

import bnw.core.bnw_objects as objs


@require_auth
def cmd_on(request):
    """ Включение доставки сообщений """
    objs.User.mupdate({'name': request.user['name']}, {'$set': {'off': False}})
    if request.user.get('off', False):
        return dict(ok=True, desc='Welcome back!')
    else:
        return dict(ok=True, desc='Welcoooome baaaack, I said.')


@require_auth
def cmd_off(request):
    """ Выключение доставки сообщений """
    objs.User.mupdate({'name': request.user['name']}, {'$set': {'off': True}})
    if request.user.get('off', False):
        return dict(ok=True, desc='See you later.')
    else:
        return dict(ok=True, desc='C u l8r!')

