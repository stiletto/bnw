# -*- coding: utf-8 -*-

from base import *
from twisted.internet import defer
import bnw_core.bnw_objects as objs

from twisted.web.xmlrpc import Proxy


import simplejson as json

#@require_auth
def cmd_search(request,text):
    """ Поиск """
    if len(text)>2048:
    	result = defer.Deferred()
        result.callback(dict(ok=False,desc='Too long.'))
        return result
    print 'querylen',len(text)
    search_service = Proxy('http://127.0.0.1:7850/')
    result = search_service.callRemote('search', text.encode('utf-8','ignore'))
    def shit(x):
        print 'got shit',x
        return x
    result.addCallback(shit)
    result.addCallback(lambda x: dict(ok=True,desc='Here it is.',format='search',result=x))
    return result
