# -*- coding: utf-8 -*-
import re
from twisted.internet import defer, reactor

USER_RE=ur'[0-9A-Za-z_-]+'
MESSAGE_RE=ur'[0-9A-Za-z]+'


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

class XmppResponse(Exception): # we do it idiotic way!
    pass

class BnwResponse(Exception): # we do it idiotic way!
    pass

class CommandParserException(Exception):
    pass

class BaseCommand(object):
    pass

class BaseParser(object):
    pass

service=None
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
                if (name in rexs) and not rexs[name][1].match(value):
                    defer.returnValue(
                        dict(ok=False,
                             desc='Option "%s" doesn''t meet the constraint "%s"' % (name,rexs[name][0]),
                             constraint=True)
                    )
            defer.returnValue((yield fun(request,*args,**kwargs)))
        return new_fun
    return damndeco
