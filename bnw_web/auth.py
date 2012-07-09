# -*- coding: utf-8 -*-
from twisted.internet import reactor
from twisted.internet import interfaces, defer
from twisted.web.server import Site, NOT_DONE_YET
from twisted.web.resource import Resource, NoResource

import tornado.options
#import tornado.twister
import tornado.web
#import tornado.escape
import logging,traceback
import simplejson as json
import txmongo
import os,random,time
import escape
from widgets import widgets
import PyRSS2Gen
#import websocket_site
from datetime import datetime

from tornado.options import define, options

import bnw_core.bnw_objects as objs
import bnw_core.post as post
from thandler import TwistedHandler

class LoginHandler(TwistedHandler):
    @defer.inlineCallbacks
    def respond(self):
        key = self.get_argument("key","")
        user=(yield objs.User.find_one({'login_key':key}))
        if user:
            if self.request.protocol == "https":
                self.set_cookie('bnw_loginkey',key,expires_days=30,secure="")
            else:
                self.set_cookie('bnw_loginkey',key,expires_days=30)
            self.redirect('/')
            defer.returnValue('')
        else:
            defer.returnValue('Bad login key')

class AuthMixin(object):
    @defer.inlineCallbacks
    def get_auth_user(self):
        if not getattr(self,'user',None):
            key = self.get_cookie('bnw_loginkey',"")
            self.user = yield objs.User.find_one({'login_key':key}) if key else None
        defer.returnValue(self.user)
        
def requires_auth(fun):
    @defer.inlineCallbacks
    def newfun(self,*args,**kwargs):
        user=yield self.get_auth_user()
        if not user:
            defer.returnValue('Requires a valid login key. Go get it in the jabber interface.')
        else:
            defer.returnValue((yield fun(self,*args,**kwargs)))
    return newfun
