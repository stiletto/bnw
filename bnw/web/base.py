# -*18^- coding: utf-8 -*-

import traceback
from time import time
from twisted.internet import defer
from twisted.words.protocols.jabber.jid import JID
import tornado.web
#import txmongo
import bnw.core.base
import bnw.core.bnw_objects as objs
import linkify
from widgets import widgets
from bnw.core.base import config


class BnwWebRequest(object):
    def __init__(self, user=None):
        self.body = None
        self.to = None
        self.jid = JID(user['jid']) if user else None
        self.user = user


def get_defargs(handler=None):
    args = {
        'linkify': linkify.linkify,
        'thumbify': linkify.thumbify,
        'config': config,
        'w': widgets,
    }
    if handler:
        args['auth_user'] = getattr(handler, 'user', None)
        args['secure'] = handler.request.protocol=="https"
    return args

class BnwWebHandler(tornado.web.RequestHandler):
    errortemplate = '500.html'

    # Fucked twisted. How to run chain without passing result?
    def passargs(self, f, *args, **kwargs):
        return f(*args, **kwargs)

    @tornado.web.asynchronous
    def get(self, *args, **kwargs):
        d = defer.Deferred()
        d.addCallback(self.passargs, *args, **kwargs)
        d.addCallbacks(self.writeandfinish, self.errorfinish)
        self.start_time = self.render_time = time()
        d.callback(self.respond)

    @tornado.web.asynchronous
    def post(self, *args, **kwargs):
        d = defer.Deferred()
        d.addCallback(self.passargs, *args, **kwargs)
        d.addCallbacks(self.writeandfinish, self.errorfinish)
        self.start_time = self.render_time = time()
        d.callback(self.respond_post)

    def respond(self, *args, **kwargs):
        """Default GET response."""
        self.set_status(500)
        return 'No GET handler'

    def respond_post(self, *args, **kwargs):
        """Default POST response."""
        self.set_status(500)
        return 'No POST handler'

    def render(self, templatename, **kwargs):
        args = get_defargs(self)
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
