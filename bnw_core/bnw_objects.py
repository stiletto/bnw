# -*- coding: utf-8 -*-
from base import get_db
from bnw_xmpp.base import send_plain
from bnw_xmpp import deliver_formatters
from twisted.internet import defer
#from bnw_xmpp.parser_redeye import requireAuthRedeye, formatMessage, formatComment
#from bnw_xmpp.parser_simplified import requireAuthSimplified, formatMessageSimple, formatCommentSimple
import txmongo,time

class WrappedDict(object):
    """Обертка для говна словаря содержащегося в поле doc."""
    def __getitem__(self, name):
        return self.doc.__getitem__(name)
    def __setitem__(self, name, value):
        return self.doc.__setitem__(name, value)
    def __delitem__(self, name):
        return self.doc.__setitem__(name)
    def __contains__(self, name):
        return self.doc.__contains__(name)
    def items(self):
        return self.doc.items()
    def iteritems(self):
        return self.doc.iteritems()
    def get(self, k, d=None):
        return self.doc.get(k, d)
    def update(self, E,  **F):
        return self.doc.update(E, **F)
    def __repr__(self):
        return self.__class__.__name__+': '+self.doc.__repr__()
    def __str__(self):
        return self.doc.__str__()
    def __unicode__(self):
        return self.doc.__unicode__()

class CollectionWrapper(object):
    def __init__(self,collection_name):
        self.collection_name = collection_name

    def __getattr__(self, db_method):
        def fn(*args, **kwargs):
            d = get_db(self.collection_name)
            d.addCallback(
                lambda collection:
                    getattr(collection, db_method)(*args, **kwargs))
            return d
        return fn

INDEX_TTL = 946080000 # one year. i don't think you will ever need to change this

class MongoObject(WrappedDict):
    """ Обертка для куска говна хранящегося в бд.
    Это чтобы опечатки не убивали."""
    # any subclass MUST define "collection"
    # 
    dangerous_fields=('_id',)
    indexes = (
        (txmongo.filter.ASCENDING("id"), True, False),
    )

    def __init__(self, src=None):
        if type(src)==str:
            raise NotImplementedError('WUT')
        elif type(src)==dict:
            self.doc=src
        else:
            self.doc={}
    
    @classmethod
    @defer.inlineCallbacks
    def find_one(cls, *args,**kwargs):
        res=yield cls.collection.find_one(*args,**kwargs)
        defer.returnValue(None if (not res) else cls(res))

    @classmethod
    @defer.inlineCallbacks
    def find(cls, *args,**kwargs):
        res=yield cls.collection.find(*args,**kwargs)
        defer.returnValue(cls(doc) for doc in res)  # wrap all documents in our class

    @classmethod
    @defer.inlineCallbacks
    def find_sort(cls, spec,sort,**kwargs):
        res=yield cls.collection.find(spec,filter=txmongo.filter.sort(sort),**kwargs)
        defer.returnValue(cls(doc) for doc in res)  # wrap all documents in our class

    @classmethod
    def mupdate(cls, spec, document, *args,**kwargs):
        if not isinstance(document,dict):
            document=document.doc
        return cls.collection.update(spec,document,*args,**kwargs)

    @defer.inlineCallbacks
    def save(cls,safe=True):
        #print cls.collection,type(cls.collection)
        id=yield (cls.collection.save(cls.doc,safe=safe))
        cls.doc['_id']=id
        defer.returnValue(id)

    @classmethod
    @defer.inlineCallbacks
    def ensure_indexes(cls):
        for idi, unique, drop_dups in cls.indexes:
            _ = yield cls.collection.create_index(txmongo.filter.sort(idi), unique=unique, dropDups=drop_dups)
        defer.returnValue(None)

    def filter_fields(self):
        msg=self.doc.copy()
        for fld in self.dangerous_fields:
            if fld in msg:
                del msg[fld]
        return msg

    def __getattr__(self,mongo_method):
        return getattr(self.collection,mongo_method)

class Message(MongoObject):
    """ Сообщение. Просто объект сообщения."""
    collection = CollectionWrapper("messages")
    dangerous_fields = ('_id','real_user')
    indexes = MongoObject.indexes + (
        (txmongo.filter.DESCENDING("date"), False, False), 
        
        (txmongo.filter.DESCENDING("user") + txmongo.filter.DESCENDING("tags") + txmongo.filter.DESCENDING("date"),
            False, False),
        (txmongo.filter.DESCENDING("user") + txmongo.filter.DESCENDING("date"), False, False),
        (txmongo.filter.DESCENDING("user") + txmongo.filter.DESCENDING("clubs") + txmongo.filter.DESCENDING("date"), False, False),
        (txmongo.filter.DESCENDING("date") + txmongo.filter.DESCENDING("recommendations"), False, False),
    )

    @defer.inlineCallbacks
    def deliver(self,target,recommender=None,recocomment=None,sfrom=None):
        feedel_val = dict(user=target['name'],message=self['id'])
        feedel = yield FeedElement.find_one(feedel_val)
        if not feedel:
            feedel_val.update(dict(recommender=recommender,
                                   recocomment=recocomment,
                                   date=time.time()))
            feedel = FeedElement(feedel_val)
            if recommender:
                formatter = deliver_formatters.parsers[target.get('interface','redeye')]['recommendation']
                         
            else:
                formatter = deliver_formatters.parsers[target.get('interface','redeye')]['message']
            formatted = formatter(None,
                dict(message=self,
                     recommender=recommender,
                     recocomment=recocomment)
            )
            _ = yield feedel.save()
            if not target.get('off',False):
                target.send_plain(formatted,sfrom)
                defer.returnValue(1)
            defer.returnValue(0)
        else:
            defer.returnValue(0)

class FeedElement(MongoObject):
    """ Элемент ленты. 
        id: id сообщения
        user: пользователь-обладатель ленты."""
    collection = CollectionWrapper("feeds")
    indexes = (
        (txmongo.filter.ASCENDING("message")+txmongo.filter.ASCENDING("user"), False, False),
    )

class Comment(MongoObject):
    """ Объект комментария."""
    collection = CollectionWrapper("comments")
    dangerous_fields = ('_id','real_user')
    indexes = MongoObject.indexes + (
        (txmongo.filter.ASCENDING("message"), False, False),
    )

    def deliver(self,target,recommender=None,recocomment=None,sfrom=None):
        if not target.get('off',False):
            formatter = deliver_formatters.parsers[target.get('interface','redeye')]['comment']
            formatted = formatter(None,
                dict(comment=self)
            )
            target.send_plain(formatted,sfrom)
            return 1 #defer.returnValue(1)
        else:
            return 0

class User(MongoObject):
    """ Няшка-пользователь."""
    collection = CollectionWrapper("users")
    dangerous_fields=('_id','login_key','avatar','jid','jids','pending_jids','id','settings')
    indexes = (
        (txmongo.filter.ASCENDING("name"), True, False),
    )
    
    def send_plain(self,message,sfrom=None):
        if self['jid']:
            send_plain(self['jid'],sfrom,message)

class Subscription(MongoObject):
    """ Сраная подписка. """
    collection = CollectionWrapper("subscriptions")
    indexes = (
        (txmongo.filter.ASCENDING("user")+txmongo.filter.ASCENDING("type"), False, False),
        (txmongo.filter.ASCENDING("target")+txmongo.filter.ASCENDING("type"), False, False),
    )

    def is_remote(self):
        return '@' in self['target']

class GlobalState(MongoObject):
    """ Всякие глобальные переменные."""
    collection = CollectionWrapper("globalstate")
    indexes = (
        (txmongo.filter.ASCENDING("name"), True, False),
    )

class Club(MongoObject):
    """ Клуб в выхлопе мап-редьюса."""
    collection = CollectionWrapper("clubs")
    indexes = ()

class Tag(MongoObject):
    """ Клуб в выхлопе мап-редьюса."""
    collection = CollectionWrapper("tags")
    indexes = ()

class Today(MongoObject):
    """ Обсуждаемый сегодня пост в выхлопе мап-редьюса."""
    collection = CollectionWrapper("today")
    indexes = ()

class Timing(MongoObject):
    """ Время выполнения."""
    collection = CollectionWrapper("timings")
    indexes = ()

class Throttle(MongoObject):
    """ Троттлинг."""
    collection = CollectionWrapper("post_throttle")
    indexes = (
        (txmongo.filter.ASCENDING("user"), True, False),
    )
