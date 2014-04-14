# -*- coding: utf-8 -*-

from base import *
import bnw.core.bnw_objects as objs

#@require_auth


@check_arg(page='[0-9]*')
def cmd_userlist(request, page=""):
    """ Список пользователей """
    page = int(page) if page else 0
    users = objs.User.find_sort({}, [('name', 1)], limit=50, skip=50 * page)
    return dict(ok=True, users=[x.filter_fields() for x in users],
        format='userlist', page=page, cache=3600, cache_public=True)
