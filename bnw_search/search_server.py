#!/usr/bin/env python
from datetime import *
import xapian

import sys

import time
from twisted.internet import defer, reactor

import re

from base64 import b64decode

#import zmq
import sys
import xapian
import indexer
 
from twisted.web import xmlrpc, server

class BnwSearchService(xmlrpc.XMLRPC):
    def __init__(self,dbname,language="russian",pulltime=None):
        xmlrpc.XMLRPC.__init__(self)
        self.language = language
        self.dbname = dbname
        self.pulltime = pulltime
        self.database = xapian.Database(self.dbname)
        self.stemmer = xapian.Stem(self.language)
        self.query_parser = xapian.QueryParser()
        self.query_parser.set_stemmer(self.stemmer)
        self.query_parser.set_stemming_strategy(xapian.QueryParser.STEM_ALL)
        self.last_index = 0

    def reindex(self):
        self.last_index = time.time()
        db = xapian.WritableDatabase(self.dbname, xapian.DB_CREATE_OR_OPEN)
        indexer.index(db, 100)
        print 'Index updated. Will reopen the database on a next query.'

    def xmlrpc_search(self,query):
        print "Received msg:", query
        if type(query)!=unicode: query = unicode(query,'utf-8','replace')
        query = self.query_parser.parse_query(query.encode('utf-8','replace'),
                    xapian.QueryParser.FLAG_PHRASE|xapian.QueryParser.FLAG_PHRASE)
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
                self.database.reopen()
                print "Database reopened"
                retry = True

        results = []
        for match in matches:
            msgid=match.document.get_value(0)
            msg=match.document.get_data()
            if len(msg)>2048:
                msg=msg[:2048]+"..."
            results.append([msgid,match.percent,unicode(msg,'utf-8','replace')])

        if self.pulltime and (time.time() > self.pulltime + self.last_index):
            reactor.callLater(0,self.reindex)
        #print 'returning:',results
        return results

def main():
    r=BnwSearchService('test/',pulltime=100)
    from twisted.internet import reactor
    reactor.listenTCP(7850, server.Site(r), interface="127.0.0.1")
    reactor.run()

if __name__ == "__main__":
    try:
        from bnw_core import base
    except:
        sys.path.append('..')
        import bnw_shell
    import config
    import bnw_core.base
    bnw_core.base.config.register(config)
    main()
