# -*- coding: utf-8 -*-
from bnw_mongo import get_db #, mongo_errors
from bnw.xmpp.base import send_plain
from base import notifiers, config
# from bnw.xmpp import deliver_formatters
from tornado.concurrent import Future
from twisted.internet import defer
from tornado import gen
from tornado.ioloop import IOLoop
import time


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

    def update(self, E, **F):
        return self.doc.update(E, **F)

    def __repr__(self):
        return self.__class__.__name__ + ': ' + self.doc.__repr__()

    def __str__(self):
        return self.doc.__str__()

    def __unicode__(self):
        return self.doc.__unicode__()

def fudef(future):
    d = defer.Deferred()
    def future_callback(f):
        e = f.exception()
        if e is None:
            d.callback(f.result())
            return
        #print 'ERRA', e
        d.errback(e)
    IOLoop.current().add_future(future, future_callback)
    return d

def fudef(future):
    d = defer.Deferred()
    def future_callback(f):
        e = f.exception()
        if e is None:
            d.callback(f.result())
            return
        #print 'ERRA', e
        d.errback(e)
    IOLoop.current().add_future(future, future_callback)
    return d

class CollectionWrapper(object):
    def __init__(self, collection_name):
        self.collection_name = collection_name
        self.collection = None

    def __getattr__(self, db_method):
        if self.collection is None:
            self.collection = get_db(self.collection_name)
        method = getattr(self.collection, db_method)
        def fn(*args, **kwargs):
            #print 'method',db_method,args,kwargs
            f = method(*args, **kwargs)
            if isinstance(f, Future):
                return fudef(f)
            return f
        return fn

INDEX_TTL = 946080000  # one year. i don't think you will ever need to change this


class MongoObjectCollectionProxy(type):
    def __getattr__(self, mongo_method):
        return getattr(self.collection, mongo_method)


class MongoObject(WrappedDict):
    """ Обертка для куска говна хранящегося в бд.
    Это чтобы опечатки не убивали."""
    __metaclass__ = MongoObjectCollectionProxy
    # any subclass MUST define "collection"
    #
    dangerous_fields = ('_id',)
    indexes = (
        ((("id",1),), True, False),
    )

    def __init__(self, src=None):
        if type(src) == str:
            raise NotImplementedError('WUT')
        elif type(src) == dict:
            self.doc = src
        else:
            self.doc = {}

    @classmethod
    @defer.inlineCallbacks
    def count(cls, *args, **kwargs):
        cursor = yield cls.collection.find(*args, **kwargs)
        res = yield fudef(cursor.count())
        defer.returnValue(res)

    @classmethod
    @defer.inlineCallbacks
    def find_one(cls, *args, **kwargs):
        res = yield cls.collection.find_one(*args, **kwargs)
        defer.returnValue(None if (not res) else cls(res))

    @classmethod
    @defer.inlineCallbacks
    def find(cls, *args, **kwargs):
        cursor = yield cls.collection.find(*args, **kwargs)
        limit = kwargs.get('limit',1000) # TODO: Document this
        res = yield fudef(cursor.to_list(limit))
        defer.returnValue(
            cls(doc) for doc in res)  # wrap all documents in our class

    @classmethod
    @defer.inlineCallbacks
    def find_sort(cls, spec, sort, **kwargs):
        cursor = yield cls.collection.find(spec, **kwargs)
        cursor.sort(sort)
        limit = kwargs.get('limit',1000) # TODO: Document this
        res = yield fudef(cursor.to_list(limit))
        #print 'findsort res ', len(res)
        defer.returnValue(
            cls(doc) for doc in res)  # wrap all documents in our class

    @classmethod
    def mupdate(cls, spec, document, *args, **kwargs):
        if not isinstance(document, dict):
            document = document.doc
        return cls.collection.update(spec, document, *args, **kwargs)

    @defer.inlineCallbacks
    def save(cls, w=1):
        # print cls.collection,type(cls.collection)
        id = yield (cls.collection.save(cls.doc, w=w))
        cls.doc['_id'] = id
        defer.returnValue(id)

    @classmethod
    @defer.inlineCallbacks
    def ensure_indexes(cls):
        for idi, unique, drop_dups in cls.indexes:
            _ = yield cls.collection.create_index(list(idi), unique=unique, dropDups=drop_dups)
        defer.returnValue(None)

    def filter_fields(self):
        msg = self.doc.copy()
        for fld in self.dangerous_fields:
            if fld in msg:
                del msg[fld]
        return msg


class Message(MongoObject):
    """ Сообщение. Просто объект сообщения."""
    collection = CollectionWrapper("messages")
    dangerous_fields = ('_id', 'real_user')
    indexes = MongoObject.indexes + (
        ((("user", 1), ("tags", 1), ("date", -1)), False, False),
        ((("user", 1), ("clubs", 1), ("date", -1)), False, False),
        ((("date", -1), ("recommendations", -1)), False, False),
    )

    def save(self, safe=True):
        print "+MESSAGE:", self.doc
        return super(Message, self).save()

    @defer.inlineCallbacks
    def deliver(self, target, recommender=None, recocomment=None, sfrom=None):
        feedel_val = dict(user=target['name'], message=self['id'])
        feedel = yield FeedElement.find_one(feedel_val)
        if not feedel:
            feedel_val.update(dict(recommender=recommender,
                                   recocomment=recocomment,
                                   date=time.time()))
            feedel = FeedElement(feedel_val)
            _ = yield feedel.save()
            res = 0
            for notifier in notifiers:
                res += yield notifier.notify(target, 'message', (self, recommender, recocomment, sfrom))
            defer.returnValue(res)
        else:
            defer.returnValue(0)


class FeedElement(MongoObject):
    """ Элемент ленты.
        id: id сообщения
        user: пользователь-обладатель ленты."""
    collection = CollectionWrapper("feeds")
    indexes = ( ((("message", 1),("user", 1)), True, False),
                ((("user", 1),("_id", -1)), True, False),
    )


class Comment(MongoObject):
    """ Объект комментария."""
    collection = CollectionWrapper("comments")
    dangerous_fields = ('_id', 'real_user')
    indexes = MongoObject.indexes + (
        ((("message", 1),), False, False),
        ((("date", 1),), False, False),
        ((("user", 1),), False, False),
    )

    def save(self, safe=True):
        print "+COMMENT:", self.doc
        return super(Comment, self).save()

    @defer.inlineCallbacks
    def deliver(self, target, recommender=None, recocomment=None, sfrom=None):
        res = 0
        for notifier in notifiers:
            res += yield notifier.notify(target, 'comment', (self, sfrom))
        defer.returnValue(res)


class User(MongoObject):
    """ Няшка-пользователь."""
    collection = CollectionWrapper("users")
    dangerous_fields = ('_id', 'login_key', 'avatar', 'jid', 'jids',
                        'pending_jids', 'id', 'settings', 'blacklist')
    indexes = (
        ((("name", 1),), True, False),
    )

    def send_plain(self, message, sfrom=None):
        if not sfrom:
            sfrom = self.get('settings', {}).get('servicejid', None)
        if self['jid']:
            send_plain(self['jid'], sfrom, message)


def massert(condition,code="assert"):
    if not condition:
        defer.returnValue((False, code))

class Subscription(MongoObject):
    """ Сраная подписка. """
    collection = CollectionWrapper("subscriptions")
    indexes = (
        ((("user", 1), ("type", 1)), False, False),
        ((("target", 1), ("type", 1)), False, False),
    )

    def is_remote(self):
        return '@' in self['target']

    @classmethod
    @defer.inlineCallbacks
    def subscribe(cls, user, target_type, target, safe=True, sfrom=None):
        massert(target_type in ('sub_club', 'sub_tag', 'sub_user', 'sub_message'))

        sub_rec = { 'user': user['name'], 'target': target, 'type': target_type }

        if sfrom:
            sub_rec['from'] = sfrom

        subject = None
        if not safe:
            pass
        elif target_type == 'sub_user':
            subject = yield User.find_one({ 'name':target })
            if not subject:
                defer.returnValue((False, "sub_nouser"))
        elif target_type == 'sub_message':
            subject = yield Message.find_one({ 'id':target })
            if not subject:
                defer.returnValue((False, "sub_nomessage"))
        try:
            yield cls.insert(sub_rec, safe=safe)
        except mongo_errors.DuplicateKeyError:
            defer.returnValue((False, "sub_exists"))
        defer.returnValue((True, subject))

    @classmethod
    @defer.inlineCallbacks
    def unsubscribe(self, user, target_type, target, safe=True):
        massert(target_type in ('sub_club', 'sub_tag', 'sub_user', 'sub_message'))
        sub_rec = { 'user': user['name'], 'target': target, 'type': target_type }
        if safe:
            result = yield cls.find_and_modify(sub_rec, remove=True)
            if result:
                defer.returnValue((True, result))
            defer.returnValue((False, "sub_nosub"))
        yield cls.remove(sub_rec)
        defer.returnValue((True, None))


class GlobalState(MongoObject):
    """ Всякие глобальные переменные."""
    collection = CollectionWrapper("globalstate")
    indexes = (
        ((("name", 1),), True, False),
    )


class Club(MongoObject):
    """ Клуб в выхлопе мап-редьюса."""
    collection = CollectionWrapper("clubs")
    indexes = ()


class StatMessages(MongoObject):
    """ Статистика по сообщениям в выхлопе мап-редьюса."""
    collection = CollectionWrapper("stat_messages")
    indexes = ()


class StatComments(MongoObject):
    """ Статистика по комментам в выхлопе мап-редьюса."""
    collection = CollectionWrapper("stat_comments")
    indexes = ()

class StatCharacters(MongoObject):
    """ Статистика по количеству символов в выхлопе мап-редьюса."""
    collection = CollectionWrapper("stat_talkers")
    indexes = ()


class Tag(MongoObject):
    """ Тег в выхлопе мап-редьюса."""
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
        ((("user", 1),), True, False),
        ((("bucket", 1),), False, False),
    )

class UserTag(Tag):
    """ Тег в выхлопе мап-редьюса."""
    collection = CollectionWrapper("usertags")
    indexes = (
        ((("user", 1), ("count", -1)), False, False),
    )
