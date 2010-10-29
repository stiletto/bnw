#!/usr/bin/env python
# -*- coding: utf-8 -*-

import couchdb
import couchdb.client
from uuid import uuid4

#db=couchdb.Server('http://10.254.230.1:5984/')['blackjack_and_whores']

class TypedDb:
    def __init__(self,db):
        self.db=db
#        couchdb.Server(url)[dbname]
    def get(self,docid,_type):
        if _type is None:
            return self.db[docid]
        try:
            if docid=="":
                raise couchdb.client.ResourceNotFound('empty docid')
            doc = self.db[docid]
        except couchdb.client.ResourceNotFound:
            return None
            #raise Exception(str(doc))
        if doc['type']!=cls._type:
            raise Exception('Cannot get. Wrong object type. "%s" is not "%s", it is "%s".' % (docid,_type,doc['type']) )
        return doc
        
    def put(self,doc,_type):
        if _type is None:
            self.db[doc['_id']]=doc
            return
        try:
            olddoc = self.db[doc['_id']]
            if olddoc['type']!=_type:
                raise Exception('Cannot update. Wrong object type. "%s" is not "%s", it is "%s".' % (doc['_id'],_type,olddoc['type']) )
        except couchdb.client.ResourceNotFound:
            pass
        self.db[doc['_id']]=doc
    
    def delete(self,docid,_type):
        doc = self.db[docid]
        if (not (_type is None)) and doc['type']!=_type:
            raise Exception('Cannot delete. Wrong object type. "%s" is not "%s", it is "%s".' % (doc['_id'],_type,doc['type']) )
        self.db.delete(doc)
