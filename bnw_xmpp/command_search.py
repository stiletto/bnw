# -*- coding: utf-8 -*-

from base import *
from twisted.internet import defer
import bnw_core.bnw_objects as objs

from functools import partial
from bnw_search import zmq_fuckup

from twisted.web.xmlrpc import Proxy

#search_service = zmq_fuckup.ZMQRequestService()
search_service = Proxy('http://127.0.0.1:7850/')
#search_service.start()

import simplejson as json

@require_auth
@defer.inlineCallbacks
def cmd_search(request,text):
    """ Поиск """
    if len(text)>2048:
        defer.returnValue(dict(ok=False,desc='Too long.'))
    #result = yield search_service.request(text.encode('utf-8','ignore'))
    result = yield search_service.callRemote('search', text.encode('utf-8','ignore'))
    print type(result)
    print repr(result)
    #result = json.loads(result)
    defer.returnValue(dict(ok=True,desc='Here it is.',format='search',result=result))
