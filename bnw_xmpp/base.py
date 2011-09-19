# -*- coding: utf-8 -*-
import re
from twisted.internet import defer, reactor
from bnw_core.delayed_global import DelayedGlobal
import bnw_core.base

USER_RE=ur'[0-9A-Za-z_-]+'

FUCK = 'http://bnw.im/' 
MESSAGE_RE=ur'(?:#|'+FUCK+ur'p/)?([0-9A-Za-z]+)'
COMMENT_RE=ur'(?:#|'+FUCK+ur'p/)?([0-9A-Za-z]+(?:#|/)[0-9A-Za-z]+)'
MESSAGE_COMMENT_RE=ur'(?:#|'+FUCK+ur'p/)?([0-9A-Za-z]+(?:(?:#|/)[0-9A-Za-z]+)?)'

MESSAGE_REC = re.compile(MESSAGE_RE)
COMMENT_REC = re.compile(COMMENT_RE)
MESSAGE_COMMENT_REC = re.compile(MESSAGE_COMMENT_RE)

def canonic_message(s):
    m=MESSAGE_REC.match(s)
    return m.group(1) if m else ""

def canonic_comment(s):
    m=COMMENT_REC.match(s)
    return m.group(1).replace('#','/') if m else ""

def canonic_message_comment(s):
    m=MESSAGE_COMMENT_REC.match(s)
    return m.group(1).replace('#','/') if m else ""

class XmppMessage(object):
    def __init__(self,body,to,jid=None,bare_jid=None,user=None):
        self.body=body
        self.to=to
        self.jid=jid
        if bare_jid is None:
            bare_jid=jid.split('/',1)[0]
        self.bare_jid=bare_jid
        self.user=user
        self.type='xmpp'

class CommandParserException(Exception):
    pass

class BaseCommand(object):
    pass

class BaseParser(object):
    pass

service = DelayedGlobal('xmpp_service')

def send_plain(dst,src,msg):
    reactor.callFromThread(service.send_plain, dst, src, msg)
    # instead of service.send_plain(dst,src,msg)
def send_raw(dst,src,msg):
    reactor.callFromThread(service.send_raw, dst, src, msg)

def _(s,user):
    return s
            
#from bnw_core.base import get_db

def require_auth(fun):
    @defer.inlineCallbacks
    def newfun(request,*args,**kwargs):
        if request.user is None:
            defer.returnValue(
                dict(ok=False,desc='Only for registered users')
            )
        else:
            defer.returnValue((yield fun(request,*args,**kwargs)))
    newfun.__doc__ = fun.__doc__
    return newfun

def check_arg(**kwargs): #fun,name,rex):
    rexs={}
    for name,value in kwargs.iteritems():
        rexc = re.compile(r'\A'+value+r'\Z',re.DOTALL|re.UNICODE|re.MULTILINE)
        rexs[name] = (value,rexc)
    def damndeco(fun):
        @defer.inlineCallbacks
        def new_fun(request,*args,**kwargs):
            for name,value in kwargs.iteritems():
                if value is None:
                    value = ''
                if (name in rexs) and not rexs[name][1].match(value):
                    defer.returnValue(
                        dict(ok=False,
                             desc='Option "%s" doesn''t meet the constraint "%s"' % (name,rexs[name][0]),
                             constraint=True)
                    )
            defer.returnValue((yield fun(request,*args,**kwargs)))
        new_fun.__doc__ = fun.__doc__
        return new_fun
    return damndeco
