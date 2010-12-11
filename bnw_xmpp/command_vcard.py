# -*- coding: utf-8 -*-
from twisted.words.xish import domish

from base import *
import random
from twisted.internet import defer

@require_auth
def cmd_vcard(request,safe=None):
    vreq = domish.Element((None, "iq"))
    vreq['type']='get'
    vreq.addChild(domish.Element((None,'vCard')))
    vreq.vCard['xmlns']='vcard-temp'
    send_raw(request.user['jid'],None,vreq)
    return dict(ok=True,desc='vCard has been requested.')
