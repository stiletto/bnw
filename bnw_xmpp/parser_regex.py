# -*- coding: utf-8 -*-


formatters = {
    'comment': None,
    'message': None,
    'recommendation': None,
    'message_with_replies': None,
    'messages': None,
}

from twisted.internet import defer

import re
import base
import parser_basexmpp

class RegexParser(parser_basexmpp.BaseXmppParser):
    def __init__(self,handlers,formatters):
        self._handlers = []
        for hnd in handlers:
            assert len(hnd) in (2,3)
            if len(hnd)==2:
                rex,handler = hnd
                kwargs = {}
            else:
                rex,handler,kwargs = hnd
            rex = '\A'+rex+'\Z'
            self._handlers.append(
                (re.compile(rex,re.UNICODE|re.MULTILINE|re.DOTALL),
                 handler,
                 kwargs))
        self.formatters = formatters

    @defer.inlineCallbacks
    def handle(self,msg):
        handler,kwargs = self.resolve(msg)
        if not handler:
            defer.returnValue('ERROR. Parser has no idea on how to handle this.')
        result=yield handler(msg,**kwargs)
        defer.returnValue(self.formatResult(msg,result))
            
    def resolve(self,msg):
        for rex,handler,kwargs in self._handlers:
            match = rex.match(msg.body)
            if match:
                args = kwargs.copy()
                args.update(match.groupdict())
                return handler,args
        else:
            return None,None
