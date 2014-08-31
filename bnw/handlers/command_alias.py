# -*- coding: utf-8 -*-
# from twisted.words.xish import domish

from base import *
import random

import bnw.core.bnw_objects as objs

ALIAS_RE = '[a-zA-Z0-9_-]+'


@require_auth
@check_arg(set=ALIAS_RE, delete=ALIAS_RE)
@defer.inlineCallbacks
def cmd_alias(request, set="", delete="", value=""):
    """ Список алиасов """
    if not (delete or (set and value)):
        defer.returnValue(
            dict(
                ok=False, desc='Usage: alias -s <alias> <command>\n\t\tor alias -d <alias>\nFor example, "alias -s fag pm -u %1 YOU ARE A FAG!" will make it easy to tell someone that he is a fag. Just "fag <user>"!')
        )

    if set:
        assert len(set) <= 32 and len(value) <= 1024
        _ = yield objs.User.mupdate({'name': request.user['name']}, {'$set': {'aliases.%s' % (set,): value}})
        defer.returnValue(
            dict(ok=True,
                         desc='Alias %s updated.' % (set,)
                 )
        )
    elif delete:
        assert len(delete) <= 32
        _ = yield objs.User.mupdate({'name': request.user['name']}, {'$unset': {'aliases.%s' % (delete,): 1}})
        defer.returnValue(
            dict(ok=True,
                         desc='Alias %s deleted.' % (delete,)
                 )
        )
