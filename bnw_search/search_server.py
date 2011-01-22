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
 
context = zmq.Context()

class BnwSearchService(object):
    def __init__(self,dbname,language="russian",bind_addr="tcp://127.0.0.1:7850"):
        self._bind_addr = bind_addr
        self.dbname = dbname
        self.language = language

    def run(self):
        database = xapian.Database(self.dbname)

        enquire = xapian.Enquire(database)
        stemmer = xapian.Stem(self.language)

        socket = context.socket(zmq.XREP)
        socket.bind(self._bind_addr)

        while True:
            msg = socket.recv_multipart()
            print "Received msg: ", msg
            if  len(msg) != 3:
                error_msg = 'invalid message received: %s' % msg
                print error_msg
                reply = [msg[0],msg[1], '0', error_msg]
                socket.send_multipart(reply)
                continue
            id0,id1 = msg[0],msg[1]
            contents = msg[2]
            terms = []
            for term in contents.strip().split(' '):
                if not term:
                    continue
                terms.append(stemmer(term.lower()))

            query = xapian.Query(xapian.Query.OP_AND, terms)
            #print dir(query)
            print "Performing query",terms #query.get_description()

            enquire.set_query(query)
            matches = enquire.get_mset(0, 10)

            results = []

            print "%i results found" % matches.get_matches_estimated()
            for match in matches:
                msgid=match.document.get_value(0)
                msg=match.document.get_data()
                if len(msg)>1280:
                    msg=msg[:128]+"..."
                results.append([msgid,match.percent,msg])
                #print " --------- %s --- %i%% ----" % (msgid, match[xapian.MSET_PERCENT])
            reply = [id0,id1,'1',json.dumps(results)]
            socket.send_multipart(reply)

def main():
    BnwSearchService('test/').run()

if __name__ == "__main__":
    main()
