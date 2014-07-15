# -*- coding: utf-8 -*-

import time
from base import *
import bnw.core.bnw_objects as objs

CLUBS_MAP = 'function() { this.clubs.forEach(function(z) { emit(z, 1);}); }'
CLUBS_REDUCE = 'function(k,vals) { var sum=0; for(var i in vals) sum += vals[i]; return sum; }'

LAST_REBUILD = 0  # TODO: Сделать умнее. Ибо в случае нескольких инстансов соснёт
CLUBS_LAST_REBUILD = 0
REBUILD_PERIOD = 3600 * 6  # Период ребилда

# TODO: Херни понаписал. Чини блджад.


def cmd_clubs(request):
    """Список клубов

    Вывод топа клубов с количеством сообщений в них

    redeye: clubs
    """
    global CLUBS_LAST_REBUILD
    rebuild = time.time() > CLUBS_LAST_REBUILD + REBUILD_PERIOD
    if rebuild:
        CLUBS_LAST_REBUILD = time.time()
        result = objs.Message.map_reduce(CLUBS_MAP, CLUBS_REDUCE, out='clubs')
    if (not rebuild) or result:
        clubs = list(x.doc for x in objs.Club.find_sort({'$nor': [{'_id': '@'}, {'_id': ''}]}, [('value', -1)], limit=20))
        return dict(ok=True, format='clubs', clubs=clubs,
                    rebuilt=rebuild, cache=3600, cache_public=True)
    else:
        return dict(ok=False, desc='Map/Reduce failed')

TAGS_MAP = 'function() { this.tags.forEach(function(z) { emit(z, 1);}); }'

# TODO: deduplicate code


def cmd_tags(request):
    """Список тегов

    Вывод топа клубов с количеством сообщений для каждого

    redeye: tags
    """
    global LAST_REBUILD
    rebuild = time.time() > LAST_REBUILD + REBUILD_PERIOD
    if rebuild:
        LAST_REBUILD = time.time()
        result = objs.Message.map_reduce(TAGS_MAP, CLUBS_REDUCE, out='tags')
    if (not rebuild) or result:
        tags = list(x.doc for x in objs.Tag.find_sort({'_id': {'$ne': ''}}, [('value', -1)], limit=20))
        return dict(ok=True, format='tags', tags=tags,
                    rebuilt=rebuild, cache=3600, cache_public=True)
    else:
        return dict(ok=False, desc='Map/Reduce failed')
