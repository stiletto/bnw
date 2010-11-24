# -*- coding: utf-8 -*-
from twisted.internet import interfaces, defer, reactor
from twisted.web.server import Site, NOT_DONE_YET
from twisted.web.resource import Resource, NoResource
import tornado.twister
import tornado.web
import logging,traceback
import os,random,time,re
import escape
import websocket
from datetime import datetime

class RoutedWebSocketHandler(websocket.WebSocketHandler):
    def openSocket(self):
        pass        
    def write(self,data):
        return self.transport.write(data)
    def finish(self):
        self.transport.loseConnection()

class ErrorSocketHandler(RoutedWebSocketHandler):
    def openSocket(self):
        self.write("Fuckoff")
        self.finish()

class FuckingWsHandler(websocket.WebSocketHandler):
    def __init__(self, transport):
        websocket.WebSocketHandler.__init__(self, transport)
        self.real_handler,args=self.transport._request.site.ws_application.get_real_handler(transport)
        reactor.callLater(0,self.real_handler.openSocket,*args) # i really do hate this sort of shit

    def frameReceived(self, frame):
        self.real_handler.frameReceived(frame)

    def frameLengthExceeded(self):
        self.real_handler.frameLengthExceeded()


    def connectionLost(self, reason):
        self.real_handler.connectionLost(reason)


class WebSocketApplication(object):
    def __init__(self,handlers):
        self.handlers=[]
        self.add_handlers(handlers)
        
    def get_real_handler(self,transport):
        path=transport._request.uri
        handler = None
        for pattern, handler_class, kwargs in self.handlers:
            match = pattern.match(path)
            if match:
                args = match.groups()
                handler = handler_class(self, transport, **kwargs)
                break
        if not handler:
            handler = ErrorSocketHandler(transport)
            args = []
        return handler,args

    def add_handlers(self, handlers):
        """Appends the given handlers to our handler list."""
        for handler_tuple in handlers:
            assert len(handler_tuple) in (2, 3)
            pattern = handler_tuple[0]
            handler = handler_tuple[1]
            if len(handler_tuple) == 3:
                kwargs = handler_tuple[2]
            else:
                kwargs = {}
            if not pattern.endswith("$"):
                pattern += "$"
            self.handlers.append((re.compile(pattern), handler, kwargs))

class HandlersGetFaker(object):
    def __init__(self,handler):
        self.handler=handler
    def get(self,key):
        return self.handler

class CombinedSite(websocket.WebSocketSite):
    """Этот класс - комбинирует TornadoSite и WebSocketSite.
       Если запрос не может быть обработан WebSocketSite,
       он обрабатывается торнадо."""
    def __init__(self,tornadoapp,wsapp):
        websocket.WebSocketSite.__init__(self,Resource())
        self.ws_application=wsapp
        self.application=tornadoapp
        self.handlers=HandlersGetFaker(FuckingWsHandler)
        
    def getResourceFor(self, request):
        #rs=Site.getResourceFor(self,request)
        if True: #isinstance(rs,NoResource):
            app = self.application
            class AdaptedResource(Resource):
                def render(self, req):
                    app(request)
                    return NOT_DONE_YET
            rs=AdaptedResource()
        return rs
    def addHandler(self,a,b):
        raise Exception('GTFO, use WebSocketApplication.handlers')
