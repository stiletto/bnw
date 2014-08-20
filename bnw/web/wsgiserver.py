#!/usr/bin/python
"""WSGI server example"""
from __future__ import print_function
from gevent.pywsgi import WSGIServer
from pprint import pprint

import cookie

def application(env, start_response):
    if env['PATH_INFO'] == '/':
        cookie.set_cookie(env, 'holy', 'crap')
        start_response('200 OK', [('Content-Type', 'text/html')])
        pprint(env)
        return ["<b>hello world</b>"]
    else:
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        return ['<h1>Not Found</h1>']


if __name__ == '__main__':
    print('Serving on 8088...')
    app = cookie.CookieAdaptor(application)
    WSGIServer(('', 8088), app).serve_forever()
