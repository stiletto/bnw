# -*- coding: utf-8 -*-

from base import *
import bnw.core.bnw_objects as objs


@require_auth
@check_arg(user=USER_RE)
def cmd_pm(request, text, user=""):
    """ Отправка приватного сообщения """
    user = user.lower()
    if len(text) > 2048:
        return dict(ok=False, desc='Too long.')
    target_user = objs.User.find_one({'name': user})
    if not target_user:
        return dict(ok=False, desc='No such user.')
    target_user.send_plain('PM from @%s:\n%s' % (request.user['name'], text))
    return dict(ok=True, desc='PM sent.')
