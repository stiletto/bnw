# -*- coding: utf-8 -*-

import time
from base import *
from twisted.internet import defer
import bnw.core.bnw_objects as objs


@defer.inlineCallbacks
def cmd_clubs(request):
    """Список клубов

    Вывод топа клубов с количеством сообщений в них

    redeye: clubs
    """

    clubs = list(x.doc for x in (yield objs.Club.find_sort({'$nor': [{'_id': '@'}, {'_id': ''}]}, [('value', -1)], limit=20)))
    defer.returnValue(dict(ok=True, format='clubs', clubs=clubs,
                      rebuilt=rebuild, cache=3600, cache_public=True))


@defer.inlineCallbacks
def cmd_tags(request):
    """Список тегов

    Вывод топа клубов с количеством сообщений для каждого

    redeye: tags
    """
    tags = list(x.doc for x in (yield objs.Tag.find_sort({'_id': {'$ne': ''}}, [('value', -1)], limit=20)))
    defer.returnValue(dict(ok=True, format='tags', tags=tags,
                      rebuilt=rebuild, cache=3600, cache_public=True))
