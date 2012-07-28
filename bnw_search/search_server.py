import xapian
from twisted.internet import defer, reactor, threads
from twisted.python import log
from twisted.web import xmlrpc
from bnw_core import bnw_objects
from bnw_search.indexer import Indexer


class RPCSearch(xmlrpc.XMLRPC):
    def __init__(self, dbpath, language):
        xmlrpc.XMLRPC.__init__(self)
        self.indexer = Indexer(dbpath, language)
        self.db = xapian.Database(dbpath)
        self.stemmer = xapian.Stem(language)
        self.query_parser = xapian.QueryParser()
        self.query_parser.set_stemmer(self.stemmer)
        self.query_parser.set_stemming_strategy(xapian.QueryParser.STEM_ALL)
        self.query_parser.add_boolean_prefix('author', 'A')
        self.query_parser.add_boolean_prefix('user', 'A')
        self.query_parser.add_boolean_prefix('type', 'XTYPE')
        self.query_parser.add_prefix('clubs', 'XCLUBS')
        self.query_parser.add_prefix('tags', 'XTAGS')
        date_proc = xapian.DateValueRangeProcessor(Indexer.DATE)
        self.query_parser.add_valuerangeprocessor(date_proc)
        self.run_incremental_indexing()

    @defer.inlineCallbacks
    def run_incremental_indexing(self):
        self.indexed = 0
        c1 = yield bnw_objects.Message.count({'indexed': {'$exists': False}})
        c2 = yield bnw_objects.Comment.count({'indexed': {'$exists': False}})
        self.total = c1 + c2
        self._run_incremental_indexing()

    @defer.inlineCallbacks
    def _run_incremental_indexing(self):
        bnw_o = bnw_objects.Message
        objs = yield bnw_o.find({'indexed': {'$exists': False}}, limit=500)
        objs = list(objs)
        if not objs:
            bnw_o = bnw_objects.Comment
            objs = yield bnw_o.find({'indexed': {'$exists': False}}, limit=500)
            objs = list(objs)
            if not objs:
                log.msg('=== Indexing is over. Will repeat an hour later. ===')
                reactor.callLater(3600, self.run_incremental_indexing)
                return

        yield threads.deferToThread(self.indexer.create_index, objs)
        ids = [obj['_id'] for obj in objs]
        yield bnw_o.mupdate(
            {'_id': {'$in': ids}}, {'$set': {'indexed': True}},
            safe=True, multi=True)
        self.indexed += len(objs)
        log.msg('Indexed %d/%d...' % (self.indexed, self.total))
        reactor.callLater(0.01, self._run_incremental_indexing)

    def xmlrpc_search(self, text):
        # TODO: Run queries in threads because it's blocking operation.
        try:
            query = self.query_parser.parse_query(text)
        except xapian.QueryParserError:
            return 0, []
        enquire = xapian.Enquire(self.db)
        enquire.set_query(query)
        results = []
        self.db.reopen()
        matches = enquire.get_mset(0, 10)
        for match in matches:
            doc = match.document
            res = {}
            res['id'] = doc.get_value(Indexer.ID)
            res['user'] = doc.get_value(Indexer.USER)
            res['date'] = float(doc.get_value(Indexer.DATE_ORIG))
            res['type'] = doc.get_value(Indexer.TYPE)
            res['tags_info'] = doc.get_value(Indexer.TAGS_INFO)
            text = doc.get_data().decode('utf-8')
            if len(text) > 2048:
                text = text[:2048] + u'\u2026'
            res['text'] = text
            res['percent'] = match.percent
            results.append(res)
        return matches.get_matches_estimated(), results
