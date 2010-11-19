# -*- coding: utf-8 -*-
from base import get_db,get_db_existing
from bnw_xmpp.base import send_plain
from twisted.internet import interfaces, defer, reactor
from bnw_xmpp.parser_redeye import requireAuthRedeye, formatMessage, formatComment
from bnw_xmpp.parser_simplified import requireAuthSimplified, formatMessageSimple, formatCommentSimple
import txmongo
from twisted.python import log
# TODO: suck cocks
class LazyRelated(object):
    """
    \todo suck cocks """
    def __getattr__(self, name):
        cache=super(LazyRelated, self).getattr('_lazy_relations_cache')
        relations=super(LazyRelated, self).getattr('_lazy_relations')
        if name in relations:
            if name in cache:
                return cache[name]
            else:
                rel=relations[name]
                obj=rel(self.__getattr__(name+'_id'))
                cache[name]=obj
                return obj
        else:
            return super(LazyRelated, self).__getattr__(name)
    def __setattr__(self, name, value):
        cache=super(LazyRelated, self).getattr('_lazy_relations_cache')
        relations=super(LazyRelated, self).getattr('_lazy_relations')
        if name in relations:
            cache[name]=value
            super(LazyRelated, self).__setattr__(name+"_id", value['id'])
        if name.endswith('_id') and (name[:-3] in self._lazy_relations):
            del cache[name[:-3]]
            return super(LazyRelated, self).__setattr__(name, value)
        else:
            return super(LazyRelated, self).__setattr__(name, value)
    def __delattr__(self, name, value):
        cache=super(LazyRelated, self).getattr('_lazy_relations_cache')
        relations=super(LazyRelated, self).getattr('_lazy_relations')
        if name in relations:
            del cache[name]
            super(LazyRelated, self).__delattr__(name+'_id')
        if name.endswith('_id') and (name[:-3] in self._lazy_relations):
            del cache[name[:-3]]
            super(LazyRelated, self).__delattr__(name)
        else:
            return super(LazyRelated, self).__delattr__(name)

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

class AdvancedWrappedDict(object):
    """This is advanced version of WrappedDict and will sometime superseed it.
    It isn't used anywhere now, so just skip to next class."""
    def __getattr__(self, name):
        sup=super(LazyRelated, self)
        if sup.__hasattr__(name) or name=='doc':
            return sup.__getattr__(name)
        else:
            return sup.__getattr__('doc').__getitem__(name)
    def __setattr__(self, name, value):
        sup=super(LazyRelated, self)
        if sup.__hasattr__(name):
            raise NotImplementedError()
        elif name=='doc':
            return sup.__setattr__(name, value)
        else:
            return sup.__getattr__('doc').__setitem__(name, value)
    def __delattr__(self, name, value):
        sup=super(LazyRelated, self)
        if sup.__hasattr__(name) or name=='doc':
            raise NotImplementedError()
        else:
            return sup.__getattr__('doc').__delitem__(name, value)
    

INDEX_TTL = 946080000 # one year. i don't think you will ever need to change this
class MongoObject(WrappedDict):
    """ Обертка для куска говна хранящегося в бд.
    Это чтобы опечатки не убивали."""
    # any subclass MUST define "collection_name"
    # 
    def __init__(self, src=None):
        self.collection=get_db_existing(self.collection_name)
        if type(src)==str:
            #_ = yield self.collection.ensure_index('id', ttl=INDEX_TTL, unique=True)
            #self.doc=yield self.collection.find_one({'id':src.lower()})
            raise NotImplementedError('sorry, i can''t load document because there is no way to defer __init__ T_T')
        elif type(src)==dict:
            self.doc=src
        else:
            self.doc={}
    
    @classmethod
    @defer.inlineCallbacks
    def find_one(self, *args,**kwargs):
        db=(yield get_db())
        res=yield db[self.collection_name].find_one(*args,**kwargs)
        defer.returnValue(None if (not res) else self(res))
        
    @classmethod
    @defer.inlineCallbacks
    def find(self, *args,**kwargs):
        db=(yield get_db())
        res=yield db[self.collection_name].find(*args,**kwargs)
        defer.returnValue(self(doc) for doc in res)  # wrap all documents in our class
    @classmethod
    @defer.inlineCallbacks
    def find_sort(self, spec,sort,**kwargs):
        db=(yield get_db())
        res=yield db[self.collection_name].find(spec,filter=txmongo.filter.sort(sort),**kwargs)
        defer.returnValue(self(doc) for doc in res)  # wrap all documents in our class

    @classmethod
    @defer.inlineCallbacks
    def remove(self, *args,**kwargs):
        db=(yield get_db())
        res=yield db[self.collection_name].remove(*args,**kwargs)
        defer.returnValue(res)

    @classmethod
    @defer.inlineCallbacks
    def mupdate(self, spec, document, *args,**kwargs):
        db=(yield get_db())
        if not isinstance(document,dict):
            document=document.doc
        res=yield db[self.collection_name].update(spec,document,*args,**kwargs)
        defer.returnValue(res)

    @defer.inlineCallbacks
    def save(self):
        id=yield self.collection.save(self.doc)
        self.doc['_id']=id
        defer.returnValue(id)
        
    @classmethod
    @defer.inlineCallbacks
    def ensure_indexes(self):
        collection=(yield get_db())[self.collection_name]
        #_ = yield collection.create_index('id', unique=True)
        idi=txmongo.filter.sort(txmongo.filter.ASCENDING("id"))
        _ = yield collection.create_index(idi, unique=True)
        defer.returnValue(None)

class Message(MongoObject):
    """ Сообщение. Просто объект сообщения."""
    collection_name = "messages"
    @defer.inlineCallbacks
    def deliver(self):
        recipients=set()
        queries=[{'target': tag, 'type': 'sub_tag'} for tag in self['tags']]
        queries+=[{'target': club, 'type': 'sub_club'} for club in self['clubs']]
        queries+=[{'target': 'anonymous' if anon else msg.user['name'], 'type': 'sub_user'}]
        for query in queries: # fuuuuuuuuuuck this will be damn slow fix it someone plz
            qn+=1
            for result in (yield get_db()).subscriptions.find(query):
                recipients.add(result['user'])
        for target_name in recipients:
            target=(yield objs.User.find_one({'name': target_name}))
            qn+=1
            if target:
                if not target.get('off',False):
                    target.send_post(message)

    @classmethod
    @defer.inlineCallbacks
    def ensure_indexes(self):
        collection=(yield get_db())[self.collection_name]
        idi=txmongo.filter.sort(txmongo.filter.ASCENDING("id"))
        _ = yield collection.create_index(idi, unique=True)
        datei=txmongo.filter.sort(txmongo.filter.DESCENDING("date"))
        _ = yield collection.create_index(datei)
        defer.returnValue(None)
        

class Comment(MongoObject):
    """ Объект комментария."""
    collection_name = "comments"

class User(MongoObject):
    """ Няшка-пользователь."""
    collection_name = "users"
    def send_comment(self,comment):
        targetif=self.get('interface','redeye')
        if targetif=='simplified':
            send_plain(self['jid'],None,formatCommentSimple(comment))
        elif targetif=='service':
            pass
        else:
            send_plain(self['jid'],None,formatComment(comment))
            
    def send_post(self,message):
        targetif=self.get('interface','redeye')
        if targetif=='simplified':
            send_plain(self['jid'],None,formatMessageSimple(message))
        else:
            send_plain(self['jid'],None,formatMessage(message))

    @classmethod
    @defer.inlineCallbacks
    def ensure_indexes(self):
        collection=(yield get_db())[self.collection_name]
        _ = yield collection.ensure_index('id', ttl=INDEX_TTL, unique=True)
        _ = yield collection.ensure_index('name', ttl=INDEX_TTL)
        defer.returnValue(None)
        
class Subscription(MongoObject):
    """ Сраная подписка. """
    collection_name = "subscriptions"

    @classmethod
    @defer.inlineCallbacks
    def ensure_indexes(self):
        collection=(yield get_db())[self.collection_name]
        _ = yield collection.ensure_index('id', ttl=INDEX_TTL, unique=True)
        _ = yield collection.ensure_index({'user':1,'type':1}, ttl=INDEX_TTL)
        defer.returnValue(None)

    def is_remote(self):
        return '@' in self['target']
