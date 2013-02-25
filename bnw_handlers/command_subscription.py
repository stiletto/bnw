# -*- coding: utf-8 -*-
# from twisted.words.xish import domish

from base import *
import random

import bnw_core.bnw_objects as objs
import bnw_core.post
import pymongo


def _(s, user):
    return s


def usageHelp(name):
    return 'Usage: %s <-u username|-t tag|-c club|-m message>' % (name,)


def parseSubscription(**kwargs):
    for stype in ['message', 'user', 'club', 'tag']:
        if kwargs.get(stype):
            return kwargs[stype], 'sub_' + stype
    return None, None

stypes = {'*': 'tag', '!': 'club', '@': 'user', '#': 'message'}
srtypes = dict((d[1], d[0]) for d in stypes.items())


@require_auth
@defer.inlineCallbacks
def cmd_subscriptions(request):
    """ Список подписок """
    defer.returnValue(
        dict(ok=True, format="subscriptions",
             subscriptions=[x.filter_fields() for x in
                     (yield objs.Subscription.find({'user': request.user['name'],
                                                    'type':{'$ne': 'sub_message'}}))
             ])
    )


@require_auth
@check_arg(user=USER_RE)
@defer.inlineCallbacks
def cmd_subscribe(request, message="", user="", tag="", club="", newtab=None):
        """ Подписка """
        user = user.lower()
        message = canonic_message(message).upper()
        tag = tag.lower()
        club = club.lower()
        starget, stype = parseSubscription(
            message=message, user=user, tag=tag, club=club)
        if not starget:
            defer.returnValue(
                dict(ok=False, desc=usageHelp('subscribe'))
            )
        if newtab:
            subc = ''.join(c for c in starget[:10] if (c >= 'a' and c <= 'z'))
            sfrom = stype[4] + '-' + subc
        else:
            sfrom = request.to.userhost() if request.to else None
        ok, desc = (yield bnw_core.post.subscribe(request.user, stype, starget, sfrom=sfrom))
        defer.returnValue(dict(ok=ok, desc=desc))


@require_auth
@check_arg(user=USER_RE)
@defer.inlineCallbacks
def cmd_unsubscribe(request, message="", user="", tag="", club="", newtab=None):
        """ Отписывание """
        # В этой функции DRY всосало по полной
        user = user.lower()
        message = canonic_message(message).upper()
        tag = tag.lower()
        club = club.lower()
        starget, stype = parseSubscription(
            message=message, user=user, tag=tag, club=club)
        if not starget:
            defer.returnValue(
                dict(ok=False, desc=usageHelp('unsubscribe'))
            )
        ok, desc = yield bnw_core.post.unsubscribe(request.user, stype, starget)
        defer.returnValue(dict(ok=ok, desc=desc))
