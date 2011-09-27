# -*- coding: utf-8 -*-

import time
from base import *
from twisted.internet import defer
import bnw_core.bnw_objects as objs

CLUBS_MAP = 'function() { this.clubs.forEach(function(z) { emit(z, 1);}); }'
CLUBS_REDUCE = 'function(k,vals) { var sum=0; for(var i in vals) sum += vals[i]; return sum; }'
                            
LAST_REBUILD = 0 # TODO: Сделать умнее. Ибо в случае нескольких инстансов соснёт
REBUILD_PERIOD = 3600*6 # Период ребилда

# TODO: Херни понаписал. Чини блджад.
@defer.inlineCallbacks
def cmd_clubs(request):
    """ Список клубов
    
    Вывод топа клубов с количеством сообщений в них

    redeye: clubs
     """
    rebuild = time.time() > LAST_REBUILD+REBUILD_PERIOD
    if rebuild:
        global LAST_REBUILD
        LAST_REBUILD = time.time()
        result = yield objs.Message.map_reduce(CLUBS_MAP,CLUBS_REDUCE,out='clubs')
    if (not rebuild) or result:
        clubs = list(x.doc for x in (yield objs.Club.find_sort({'$nor': [ {'_id':'@'}, {'_id':''}]},[('value',-1)],limit=20)))
        defer.returnValue(dict(ok=True,format='clubs',clubs=clubs,rebuilt=rebuild,cache=3600,cache_public=True))
    else:
        defer.returnValue(dict(ok=False,desc='Map/Reduce failed'))

TAGS_MAP = 'function() { this.tags.forEach(function(z) { emit(z, 1);}); }'

# TODO: deduplicate code
@defer.inlineCallbacks
def cmd_tags(request):
    """ Список тегов
    
    Вывод топа клубов с количеством сообщений для каждого

    redeye: tags
     """
    rebuild = time.time() > LAST_REBUILD+REBUILD_PERIOD
    if rebuild:
        global LAST_REBUILD
        LAST_REBUILD = time.time()
        result = yield objs.Message.map_reduce(TAGS_MAP,CLUBS_REDUCE,out='tags')
    if (not rebuild) or result:
        tags = list(x.doc for x in (yield objs.Tag.find_sort({'_id':{'$ne':''}},[('value',-1)],limit=20)))
        defer.returnValue(dict(ok=True,format='tags',tags=tags,rebuilt=rebuild,cache=3600,cache_public=True))
    else:
        defer.returnValue(dict(ok=False,desc='Map/Reduce failed'))
