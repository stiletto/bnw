# -*- coding: utf-8 -*-
#epollreactor.install()

import os,random,time
import escape
import json
from twisted.internet import defer
from widgets import widgets
from datetime import datetime
from tornado.escape import utf8,_unicode
from escape import linkify

import bnw_core.bnw_objects as objs
import bnw_core.post as post
import bnw_core.base
from bnw_handlers.command_show import cmd_feed

from base import BnwWebHandler, TwistedHandler, BnwWebRequest
from auth import LoginHandler, requires_auth, AuthMixin

import api_handlers

class ApiRequest(object):
    def __init__(self,body,jid=None,user=None):
        self.body=body
        self.to=None
        self.jid=jid
        if jid:
            self.bare_jid=jid.split('/',1)[0]
        else:
            self.bare_jid=None
        self.user=user
        if user and not jid:
            self.jid = user['jid']
        self.type='http-api'


class ApiHandler(BnwWebHandler):
    templatename='api.html'
    @defer.inlineCallbacks
    def respond_post(self,cmd_name):
        user=yield objs.User.find_one({'login_key':self.get_argument("login","")})
        if not cmd_name:
            defer.returnValue(json.dumps(dict(ok=True,commands=api_handlers.handlers.keys())))
        if not (cmd_name in api_handlers.handlers):
            defer.returnValue('{ok: False, desc: "command unknown"}')
        handler = api_handlers.handlers[cmd_name]
        args = dict((utf8(k),_unicode(v[0])) for k,v in self.request.arguments.iteritems())
        if 'login' in args:
            del args['login']
        req = ApiRequest('',None,user)
        self.set_header("Cache-Control", "no-cache")
        try:
            result = yield handler(req,**args)
        except bnw_core.base.BnwResponse, br:
            defer.returnValue(json.dumps({'ok':False,'desc':str(br)},ensure_ascii=False))
        defer.returnValue(json.dumps(result,ensure_ascii=False))
    respond = respond_post
    def check_xsrf_cookie(self):
        pass
