import traceback
from twisted.web.server import Site, NOT_DONE_YET
from twisted.web.resource import Resource
from twisted.internet import reactor

import sys
sys.path.append('..')
import bnw_shell

from tornado.escape import url_unescape
from functools import *

from zmq_fuckup import ZMQRequestService

class SearchResource(Resource):
    def __init__(self,rs=None):
        Resource.__init__(self)
        if not rs:
            rs = ZMQRequestService()
        self.rs = rs
        rs.start()

    def __del__(self):
        self.rs.stop()

    def render_GET(self,request):
        args = request.args.get('q',[''])[0]
        if not args:
            request.setResponseCode(200)
            return 'Where is your fucking search query?!'

        text = url_unescape(args)
        cb = partial(self._cb_render_GET,request)
        self.rs.request(cb,text.encode('utf-8','ignore'))
        return NOT_DONE_YET
        
    def _cb_render_GET(self,request,result):
        request.write(result)
        request.finish()
        print '<',result
        
    def getChild(self,*args,**kwargs):
        return self

def main():
    from twisted.web import server
    r = SearchResource()
    reactor.listenTCP(7080, server.Site(r))
    reactor.run()
    #r.tp.stop()

if __name__ == '__main__':
    main()
