# -*- coding: utf-8 -*-

from base import *
from bnw.core.base import get_webui_base
import bnw.core.bnw_objects as objs


@require_auth
def cmd_login(request):
    """ Логин-ссылка """
    return dict(
        ok=True,
        desc='%s/login?key=%s' % (
            get_webui_base(request.user),
            request.user.get('login_key', '')))


def cmd_passlogin(request, user=None, password=None):
    """ Логин паролем """
    if not (user and password):
        return dict(ok=False, desc='Credentials cannot be empty.')
    u = objs.User.find_one({'name': user, 'settings.password': password})
    if u:
        return dict(ok=True, desc=u.get('login_key', 'Successful, but no login key.'))
    else:
        return dict(ok=False, desc='Sorry, Dave.')
