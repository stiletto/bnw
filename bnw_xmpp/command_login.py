# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

from base import *
import bnw_core.base
import bnw_core.bnw_objects as objs
from twisted.internet import defer

@require_auth
def cmd_login(request):
    return dict(ok=True,
             desc=bnw_core.base.config.webui_base+'login?key='+request.user.get('login_key',''))

@defer.inlineCallbacks
def cmd_passlogin(request,user,password):
    if not (user and password):
        defer.returnValue(dict(ok=False,desc='Credentials cannot be empty'))
    u = yield objs.User.find_one({'name':user,'settings.password':password})
    if u:
        defer.returnValue(dict(ok=True,
             desc=u.get('login_key','Successful, but no login key.')))
    else:
        defer.returnValue(dict(ok=False,
             desc='Sorry, Dave.'))
        
