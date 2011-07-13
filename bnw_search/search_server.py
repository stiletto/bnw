#!/usr/bin/env python
from datetime import *
import xapian

import sys
sys.path.append('..')
import bnw_shell

import time
from twisted.internet.protocol import Protocol, Factory
from twisted.web import resource
from twisted.web.static import File
from twisted.internet import defer, reactor

from bnw_core import base
from bnw_core import bnw_objects as objs
import re

import urllib
import traceback
import Queue
from StringIO import StringIO
from base64 import b64decode
from twisted.web.server import Site, NOT_DONE_YET
from twisted.web.resource import Resource
from twisted.python.threadpool import ThreadPool

import zmq
import simplejson  as json
import sys
import xapian
 
from twisted.web import xmlrpc, server

class BnwSearchService(xmlrpc.XMLRPC):
    def __init__(self,dbname,language="russian"):
        xmlrpc.XMLRPC.__init__(self)
        self.language = language
        self.dbname = dbname
        self.database = xapian.Database(self.dbname)
        self.stemmer = xapian.Stem(self.language)
        self.query_parser = xapian.QueryParser()
        self.query_parser.set_stemmer(self.stemmer)
        
    def xmlrpc_search(self,query):
        print "Received msg:", query
        if type(query)!=unicode: query = unicode(query,'utf-8','replace')
        query = self.query_parser.parse_query(query.encode('utf-8','replace'))
        retry = True
        enquire = xapian.Enquire(self.database)
        while retry:
            try:
                retry = False
                #print dir(query)
                print "Performing query", query
                enquire.set_query(query)
                matches = enquire.get_mset(0, 10)
                print "%i results found" % matches.get_matches_estimated()
            except xapian.DatabaseModifiedError:
                database.reopen()
                print "Database reopened"
                retry = True

        results = []
        for match in matches:
            msgid=match.document.get_value(0)
            msg=match.document.get_data()
            if len(msg)>2048:
                msg=msg[:2048]+"..."
            results.append([msgid,match.percent,unicode(msg,'utf-8','replace')])
        return results

def main():
    r=BnwSearchService('test/')
    from twisted.internet import reactor
    reactor.listenTCP(7850, server.Site(r), interface="127.0.0.1")
    reactor.run()

if __name__ == "__main__":
    main()
