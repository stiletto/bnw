# -*- coding: utf-8 -*-
import re
from twisted.internet import defer, reactor
from bnw_core.delayed_global import DelayedGlobal
import bnw_core.base

class XmppMessage(object):
    def __init__(self,body,to,jid=None,user=None):
        self.body=body
        self.to=to
        self.jid=jid
        self.user=user
        self.type='xmpp'

class CommandParserException(Exception):
    pass

class BaseParser(object):
    pass

service = DelayedGlobal('xmpp_service')

def send_plain(dst,src,msg):
    reactor.callFromThread(service.send_plain, dst, src, msg)
    # instead of service.send_plain(dst,src,msg)

def send_raw(dst,src,msg):
    reactor.callFromThread(service.send_raw, dst, src, msg)
