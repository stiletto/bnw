# -*- coding: utf-8 -*-
import tornado.web
import traceback
import txmongo

import bnw_core.bnw_objects as objs

class BnwWebRequest(object):
    def __init__(self,user=None):
        self.body=None
        self.to=None
        self.jid=user['jid']
        self.bare_jid=self.jid
        self.user=user


class TwistedHandler(tornado.web.RequestHandler):
    def writeandfinish(self,text):
        if not self._finished:
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
    
    @tornado.web.asynchronous
    def get(self,*args,**kwargs):
        try:
            self.respond(*args,**kwargs).addCallbacks(self.writeandfinish,self.errorfinish)
        except Exception:
            self.write(traceback.format_exc())
            self.finish()

    @tornado.web.asynchronous
    def post(self,*args,**kwargs):
        try:
            self.respond_post(*args,**kwargs).addCallbacks(self.writeandfinish,self.errorfinish)
        except Exception:
            self.write(traceback.format_exc())
            self.finish()
