import json
import time
from twisted.internet import defer
from tornado.escape import utf8, _unicode
from bnw_core.base import BnwResponse
import bnw_core.bnw_objects as objs
from bnw_web.base import BnwWebRequest, BnwWebHandler
import api_handlers


class ApiRequest(BnwWebRequest):
    def __init__(self, user=None):
        super(ApiRequest, self).__init__(user)
        self.type = 'http-api'


class ApiHandler(BnwWebHandler):
    @defer.inlineCallbacks
    def respond_post(self, cmd_name):
        stime = time.time()
        user = yield objs.User.find_one(
            {'login_key': self.get_argument('login', '')})
        self.set_header('Content-Type', 'application/json; charset=utf-8')
        if not cmd_name:
            defer.returnValue(json.dumps(dict(
                ok=True,
                commands=api_handlers.handlers.keys())))
        if cmd_name not in api_handlers.handlers:
            defer.returnValue(json.dumps(dict(
                ok=False,
                desc='unknown command')))
        callogtuple = (id(self), cmd_name, user['name'] if user else '')
        print "API call %d '%s' by '%s' started." % callogtuple
        handler = api_handlers.handlers[cmd_name]
        args = dict(
            (utf8(k), _unicode(v[0]))
            for k, v in self.request.arguments.iteritems())
        if 'login' in args:
            del args['login']
        self.set_header('Cache-Control', 'no-cache')
        cors_origin = self.request.headers.get('Origin', None)
        if cors_origin:
            self.set_header('Access-Control-Allow-Origin', '*')
            print "API call %d '%s' by '%s' is CORS from '%s'" % (callogtuple + (cors_origin,))
        try:
            result = yield handler(ApiRequest(user), **args)
        except BnwResponse as br:
            print "API call %d '%s' by '%s' failed with exception. %f.s" % (callogtuple + ((time.time() - stime),))
            defer.returnValue(json.dumps(dict(
                ok=False,
                desc=str(br)), ensure_ascii=False))
        print "API call %d '%s' by '%s' completed. %f.s" % (callogtuple + ((time.time() - stime),))
        defer.returnValue(json.dumps(result, ensure_ascii=False))

    # GET handler is the same as POST.
    respond = respond_post

    def check_xsrf_cookie(self):
        # Disable XSRF checking.
        pass
