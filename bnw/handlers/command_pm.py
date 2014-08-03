# -*- coding: utf-8 -*-

from base import *
from twisted.internet import defer
import bnw.core.bnw_objects as objs
from throttle import throttle_check


@require_auth
@check_arg(user=USER_RE)
@defer.inlineCallbacks
def cmd_pm(request, text, user=""):
    """ Отправка приватного сообщения """
    yield throttle_check(request.user['name'])
    user = user.lower()
    if len(text) > 2048:
        defer.returnValue(dict(ok=False, desc='Too long.'))
    target_user = yield objs.User.find_one({'name': user})
    if not target_user:
        defer.returnValue(dict(ok=False, desc='No such user.'))
    target_user.send_plain('PM from @%s:\n%s' % (request.user['name'], text))
    defer.returnValue(dict(ok=True, desc='PM sent.'))
