# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

from base import *
from bnw_core.base import get_webui_base
import bnw_core.bnw_objects as objs
from twisted.internet import defer

@require_auth
def cmd_login(request):
    """ Логин-ссылка """
    return dict(
        ok=True,
        desc='%s/login?key=%s' % (
            get_webui_base(request.user),
            request.user.get('login_key', '')))

@defer.inlineCallbacks
def cmd_passlogin(request,user=None,password=None):
    """ Логин паролем """
    if not (user and password):
        defer.returnValue(dict(ok=False,desc='Credentials cannot be empty.'))
    u = yield objs.User.find_one({'name':user,'settings.password':password})
    if u:
        defer.returnValue(dict(ok=True,
             desc=u.get('login_key','Successful, but no login key.')))
    else:
        defer.returnValue(dict(ok=False,
             desc='Sorry, Dave.'))
        
