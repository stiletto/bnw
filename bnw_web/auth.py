from twisted.internet import defer
import bnw_core.bnw_objects as objs
from bnw_web.base import BnwWebHandler


class LoginHandler(BnwWebHandler):
    @defer.inlineCallbacks
    def respond(self):
        key = self.get_argument('key', '')
        user = yield objs.User.find_one({'login_key': key})
        if user:
            if self.request.protocol == 'https':
                self.set_cookie(
                    'bnw_loginkey', key, expires_days=30, secure=True)
            else:
                self.set_cookie('bnw_loginkey', key, expires_days=30)
            self.redirect('/')
        else:
            defer.returnValue('Bad login key')


class LogoutHandler(BnwWebHandler):
    def respond(self):
        self.clear_all_cookies()
        self.redirect('/')


class AuthMixin(object):
    @defer.inlineCallbacks
    def get_auth_user(self):
        if not getattr(self, 'user', None):
            key = self.get_cookie('bnw_loginkey', '')
            self.user = yield objs.User.find_one({'login_key': key}) \
                if key else None
        defer.returnValue(self.user)


def requires_auth(fun):
    @defer.inlineCallbacks
    def newfun(self, *args, **kwargs):
        user=yield self.get_auth_user()
        if not user:
            defer.returnValue(
                'Requires a valid login key. '
                'Go get it in the jabber interface.')
        else:
            defer.returnValue((yield fun(self, *args, **kwargs)))
    return newfun
