# -*18^- coding: utf-8 -*-

import traceback
from time import time
import falcon
import os.path
from tornado import template, escape
from Cookie import SimpleCookie
#import txmongo
import bnw.core.base
import bnw.core.bnw_objects as objs
import linkify
from widgets import widgets
from bnw.core.base import config
import cookie

settings = {
    "template_path": os.path.join(os.path.dirname(__file__), "templates"),
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
}

class BnwWebRequest(object):
    def __init__(self, user=None):
        self.body = None
        self.to = None
        self.jid = user['jid'] if user else None
        self.user = user

def get_defargs(req=None, res=None):
    def set_xsrf_cookie(value):
        c = cookie.set_cookie(req.env, '_xsrf', value)
        if req.protocol == 'https':
            c['secure'] = True
        c['expires'] = datetime.utcnow() + timedelta(days=30)

    def get_xsrf_token():
        if 'bnw.xsrf_token' not in req.env:
            try:
                token_cookie = req.env['cookies']['_xsrf'].value
            except KeyError:
                req.env['bnw.xsrf_token'] = axsrf.Token()
            else:
                req.env['bnw.xsrf_token'] = axsrf.Token(token_cookie)
        return req.env['bnw.xsrf_token'].encoded

    def xsrf_form_html():
        return '<input type="hidden" name="_xsrf" value="' + \
            escape.xhtml_escape(get_xsrf_token()) + '"/>'

    args = {
        'linkify': linkify.linkify,
        'thumbify': linkify.thumbify,
        'config': config,
        'w': widgets,
        'xsrf_form_html': xsrf_form_html,
            static_url=self.static_url,
    }
    if req:
        args['auth_user'] = req.env.get('bnw.user')
        args['secure'] = req.protocol=="https"
        args['request'] = req
    return args

class BnwWebHandler:
    def render(self, req, templatename, **kwargs):
        args = get_defargs(req)
        args.update(kwargs)
        return super(BnwWebHandler, self).render(templatename, **args)

    def writeandfinish(self, text):
        self.render_time = time()
        if isinstance(text, dict):
            try:
                self.render(self.templatename, **text)
            except Exception:
                handlerclass = self.__class__.__name__
                self.set_status(500)
                self.render(self.errortemplate, text=traceback.format_exc(),
                            handlerclass=handlerclass)
        else:
            # TODO: We shouldn't use private variables.
            if not self._finished:
                self.write(text)
                self.finish()
        self.logperformance()

    def errorfinish(self, text):
        self.render_time = time()
        text = text.getTraceback()
        handlerclass = self.__class__.__name__
        self.set_status(500)
        self.render(self.errortemplate, text=text, handlerclass=handlerclass)
        self.logperformance()

    def logperformance(self):
        end_time = time()
        print 'PERFORMANCE',self.render_time-self.start_time, end_time-self.render_time, self.request.uri

    def static_url(self, path, include_host=None):
        if self.request.host in (config.webui_base, 'www'+config.webui_base) and self.request.protocol=="http":
            path = tornado.web.RequestHandler.static_url(self, path, False)
            return self.request.protocol + "://" + config.webui_static + path
        return tornado.web.RequestHandler.static_url(self, path, include_host)
