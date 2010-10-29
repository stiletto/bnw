from twisted.internet import epollreactor
#epollreactor.install()
from twisted.internet import reactor
from twisted.internet import interfaces, defer

import tornado.options
import tornado.twister
import tornado.web
import logging,traceback,json
import txmongo

from tornado.options import define, options

import bnw_core.bnw_objects as objs
from bnw_core.base import get_db
define("port", default=8888, help="run on the given port", type=int)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world!")

class TwistedHandler(tornado.web.RequestHandler):
    def writeandfinish(self,text):
        self.write(text)
        self.finish()
    def errorfinish(self,text):
        print 'ALARM'
        if isinstance(text,Exception):
            self.write(str(text))
        else:
            self.write(str(text))
        self.finish()
    def json_fuckup(self,dct):
        if isinstance(dct,objs.MongoObject):
            return dct.doc
        if isinstance(dct,txmongo.ObjectId):
            return str(dct)
        else:
            raise TypeError(str(type(dct)))

class MessageHandler(TwistedHandler):
    @tornado.web.asynchronous
    def get(self,query):
        try:
            self.respond(query).addCallbacks(self.writeandfinish,self.errorfinish)
        except Exception:
            self.write(traceback.format_exc())
            self.finish()

    @defer.inlineCallbacks
    def respond(self,query):
        #_ = yield objs.Message.ensure_indexes()
        f = txmongo.filter.sort(txmongo.filter.DESCENDING("date"))
        shitres=list((yield objs.Message.find(limit=20,filter=f)))
        defer.returnValue(json.dumps(shitres,default=self.json_fuckup,indent=4))

def get_site():
    application = tornado.web.Application([
        (r"/posts/(.*)", MessageHandler),
    ])

    site = tornado.twister.TornadoSite(application)
    return site

def main():
    tornado.options.parse_command_line()
    site = get_site()
    reactor.listenTCP(options.port, site)

    reactor.run()

if __name__ == "__main__":
    main()
