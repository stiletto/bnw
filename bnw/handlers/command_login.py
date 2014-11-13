# -*- coding: utf-8 -*-
# from twisted.words.xish import domish

from base import *
from bnw.core.base import get_webui_base
import bnw.core.bnw_objects as objs
from twisted.internet import defer
from throttle import throttle_check
from uuid import uuid4


@require_auth
@defer.inlineCallbacks
def cmd_login(request,reset=""):
    """ Логин-ссылка """
    user = request.user
    if reset:
        yield throttle_check(request.user['name'])
        user = yield objs.User.find_and_modify({'name': request.user['name']}, {'$set': {'login_key': uuid4().hex}}, new=True)
    defer.returnValue(dict(
        ok=True,
        desc='%s/login?key=%s' % (
            get_webui_base(user),
            user.get('login_key', ''))))


@defer.inlineCallbacks
def cmd_passlogin(request, user=None, password=None):
    """ Логин паролем """
    if not (user and password):
        defer.returnValue(dict(ok=False, desc='Credentials cannot be empty.'))
    user = canonic_user(user)
    u = yield objs.User.find_one({'name': user, 'settings.password': password})
    if u:
        defer.returnValue(dict(ok=True,
                               desc=u.get('login_key', 'Successful, but no login key.')))
    else:
        defer.returnValue(dict(ok=False,
                               desc='Sorry, Dave.'))
