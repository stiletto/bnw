# -*- coding: utf-8 -*-

import traceback
from twisted.internet import defer
import tornado.web
import txmongo
import bnw_core.base
import bnw_core.bnw_objects as objs
import linkify
from widgets import widgets


class BnwWebRequest(object):
    def __init__(self, user=None):
        self.body = None
        self.to = None
        self.jid = user['jid'] if user else ''
        self.bare_jid = self.jid.split('/', 1)[0]
        self.user = user


def get_defargs():
    return {
        'linkify': linkify.linkify,
        'thumbify': linkify.thumbify,
        'config': bnw_core.base.config,
        'w': widgets,
    }.copy()


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
        d.callback(self.respond)

    @tornado.web.asynchronous
    def post(self, *args, **kwargs):
        d = defer.Deferred()
        d.addCallback(self.passargs, *args, **kwargs)
        d.addCallbacks(self.writeandfinish, self.errorfinish)
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
        args = get_defargs()
        args['auth_user'] = getattr(self, 'user', None)
        args.update(kwargs)
        return super(BnwWebHandler, self).render(templatename, **args)

    def writeandfinish(self, text):
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

    def errorfinish(self, text):
        text = text.getTraceback()
        handlerclass = self.__class__.__name__
        self.set_status(500)
        self.render(self.errortemplate, text=text, handlerclass=handlerclass)
