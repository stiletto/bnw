from datetime import datetime, timedelta
from Cookie import SimpleCookie
import falcon
import bnw.core.bnw_objects as objs
from bnw.web.base import BnwWebHandler

class LoginHandler:#(BnwWebHandler):
    def on_get(self, req, resp):
        key = req.get_param('key', required=True)
        user = objs.User.find_one({'login_key': key})
        if user:
            cookies = SimpleCookie()
            cookies['bnw_loginkey'] = key
            cookie = cookies['bnw_loginkey']
            if req.protocol == 'https':
                cookie['secure'] = True
            cookie['expires'] = datetime.utcnow() + timedelta(days=30)
            resp.set_header('Set-Cookie', cookie.OutputString())
            resp.location = '/'
            resp.status_code = falcon.HTTP_303
        else:
            resp.status_code = falcon.HTTP_403
            resp.body = 'Bad login key'


class LogoutHandler:#(BnwWebHandler):
    def on_get(self, req, resp):
        key = req.get_param('key', required=True)
        user = objs.User.find_one({'login_key': key})
        cookies = SimpleCookie()
        cookies['bnw_loginkey'] = ''
        cookie = cookies['bnw_loginkey']
        if req.protocol == 'https':
            cookie['secure'] = True
        expires = datetime.utcnow() - timedelta(days=365)
        cookie['expires'] = expires
        resp.set_header('Set-Cookie', cookie.OutputString())
        resp.location = '/'
        resp.status_code = falcon.HTTP_303

def get_auth_user(req):
    if 'bnw.user' not in req.env:
        cookie_header = req.get_header('Cookie')
        cookies = SimpleCookie(cookie_header)
        try:
            key = cookies['bnw_loginkey'].value
        except KeyError:
            req.env['bnw.user'] = None
        else:
            req.env['bnw.user'] = objs.User.find_one({'login_key': key})
    return req.env['bnw.user']

class BnwNotAuthorized(Exception):
    @staticmethod
    def handle(ex, req, resp, params):
        pass

def requires_auth(req, resp, params):
    user = get_auth_user(req)
    if not user:
        raise BnwNotAuthorized()
