# -*- coding: utf-8 -*-

from base import *
from twisted.internet import defer
import bnw.core.bnw_objects as objs

#@require_auth


@check_arg(page='[0-9]*')
@defer.inlineCallbacks
def cmd_userlist(request, page=""):
    """ Список пользователей """
    page = int(page) if page else 0
    users = yield objs.User.find_sort({}, [('name', 1)], limit=50, skip=50 * page)
    defer.returnValue(dict(ok=True, users=[x.filter_fields(
    ) for x in users], format='userlist', page=page, cache=3600, cache_public=True))
