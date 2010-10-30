# -*- coding: utf-8 -*-
import random,time
from twisted.internet import interfaces, defer, reactor

class XmppMessage(object):
    def __init__(self,body,jid=None,bare_jid=None,user=None):
        self.body=body
        self.jid=jid
        if bare_jid is None:
            bare_jid=jid.split('/',1)[0]
        self.bare_jid=bare_jid
        self.user=user

class XmppResponse(Exception): # we do it idiotic way!
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

idchars='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    
def _(s,user):
    return s
            
import pymongo
connection=None
def get_db():
    global connection
    if connection is None:
        connection = pymongo.Connection()['bnw']
    return connection
