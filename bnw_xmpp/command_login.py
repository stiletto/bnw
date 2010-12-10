# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

from base import *
import bnw_core.base
from twisted.internet import defer

@require_auth
def cmd_login(request):
    return dict(ok=True,
             desc=bnw_core.base.config.webui_base+'login?key='+request.user.get('login_key',''))
