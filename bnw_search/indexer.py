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

WORD_RE = re.compile(ur"\w{1,32}", re.U)
ARTICLE_ID = 0

stemmer = xapian.Stem("russian") # english stemmer

def create_document(message):
    """Gets an article object and returns
    a Xapian document representing it and
    a unique article identifier."""

    doc = xapian.Document()
    text = message['text']#.encode("utf8")

    # go word by word, stem it and add to the
    # document.
    for index, term in enumerate(WORD_RE.finditer(text)):
        doc.add_posting(
          stemmer(term.group()),
          index)
    doc.add_term("A"+message['user'])
    doc.set_data(text)
    #doc.add_term("S"+message['article.subject.encode("utf8"))
    article_id_term = 'I'+message['id']
    doc.add_term(article_id_term)
    doc.add_value(ARTICLE_ID, str(message['id']))
    return doc, article_id_term

@defer.inlineCallbacks
def index(db,period):
    """Index all articles that were modified
    in the last <period> hours into the given
    Xapian database"""

    query = {'indexed': {'$ne': 1}}
    if period:
        start = time.time()-3600*period
        query['date']= { '$gte': start}

    skip = 0
    while True:
        print '-- Messages %d-%d' % (skip,skip+20)
        messages = list((yield objs.Message.find(query))) #,skip=skip,limit=20)))

        if len(messages)==0:
            break

        for message in messages:
            print message['id']
            _ = yield objs.Message.mupdate({'id':message['id']},{'$set':{'indexed':1}},safe=True)
            doc, id_term = create_document(message)
            db.replace_document(id_term, doc)
        skip += 20
        break
    reactor.stop()

if __name__=="__main__":
    #configfile, dbpath, period = sys.argv[1:]
    db = xapian.WritableDatabase('test/',
        xapian.DB_CREATE_OR_OPEN)
    index(db, 10000)
    reactor.run()
