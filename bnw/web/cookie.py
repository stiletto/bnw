from Cookie import SimpleCookie

class CookieAdaptor(object):
    def __init__(self, app):
        self.app = app
    def __call__(self, environ, start_response):
        cookie_header = environ.get('HTTP_COOKIE','')
        environ['cookies'] = SimpleCookie(cookie_header)
        set_cookies = SimpleCookie()
        def _start_response(status, response_headers, exc_info=None):
            new_headers = list(response_headers)
            for key, value in set_cookies.iteritems():
                new_headers.append(('Set-Cookie', value.OutputString()))
            return start_response(status, new_headers, exc_info)
        environ['set_cookies'] = set_cookies
        return self.app(environ, _start_response)

def set_cookie(env, name, value):
    env['set_cookies'][name] = value
    return env['set_cookies'][name]
