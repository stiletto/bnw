#!/usr/bin/python
import logging
import time
import xapian

from bnw.core import bnw_objects
from bnw.search.indexer import Indexer


class RPCSearch(object):
    def __init__(self, dbpath, language):
        self.indexer = Indexer(dbpath, language)
        self.db = xapian.Database(dbpath)
        self.stemmer = xapian.Stem(language)
        self.query_parser = xapian.QueryParser()
        self.query_parser.set_stemmer(self.stemmer)
        self.query_parser.set_stemming_strategy(xapian.QueryParser.STEM_ALL)
        self.query_parser.add_boolean_prefix('author', '@')
        self.query_parser.add_boolean_prefix('user', '@')
        self.query_parser.add_boolean_prefix('type', 'XTYPE')
        self.query_parser.add_prefix('clubs', 'XCLUBS')
        self.query_parser.add_prefix('tags', 'XTAGS')
        date_proc = xapian.DateValueRangeProcessor(Indexer.DATE)
        self.query_parser.add_valuerangeprocessor(date_proc)

    def run_incremental_indexing(self):
        self.indexed = 0
        c1 = bnw_objects.Message.count({'indexed': {'$exists': False}})
        c2 = bnw_objects.Comment.count({'indexed': {'$exists': False}})
        self.total = c1 + c2
        self._run_incremental_indexing()

    def _run_incremental_indexing(self):
        while True:
            bnw_o = bnw_objects.Message
            objs = bnw_o.find({'indexed': {'$exists': False}}, limit=500)
            objs = list(objs)
            if not objs:
                bnw_o = bnw_objects.Comment
                objs = bnw_o.find({'indexed': {'$exists': False}}, limit=500)
                objs = list(objs)
                if not objs:
                    logging.info('=== Indexing is over. Will repeat an hour later. ===')
                    return

            self.indexer.create_index(objs)
            ids = [obj['_id'] for obj in objs]
            bnw_o.mupdate(
                {'_id': {'$in': ids}}, {'$set': {'indexed': True}},
                multi=True)
            self.indexed += len(objs)
            logging.info('Indexed %d/%d...' % (self.indexed, self.total))
            #time.sleep(0.01)

    PAGE_SIZE = 20

    def xmlrpc_search(self, text, page):
        # TODO: Run queries in threads because it's blocking operation.
        if page < 0:
            return
        try:
            query = self.query_parser.parse_query(text)
        except xapian.QueryParserError:
            return
        enquire = xapian.Enquire(self.db)
        enquire.set_query(query)
        self.db.reopen()

        def process_match(match):
            doc = match.document
            return dict(
                id=doc.get_value(Indexer.ID),
                user=doc.get_value(Indexer.USER),
                date=float(doc.get_value(Indexer.DATE_ORIG)),
                type=doc.get_value(Indexer.TYPE),
                tags_info=doc.get_value(Indexer.TAGS_INFO),
                text=doc.get_data().decode('utf-8'),
                percent=match.percent)

        matches = enquire.get_mset(page * self.PAGE_SIZE, self.PAGE_SIZE)
        estimated = matches.get_matches_estimated()
        results = map(process_match, matches)
        return dict(estimated=estimated, results=results)

