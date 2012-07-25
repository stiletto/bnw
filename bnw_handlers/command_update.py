# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

from base import *
import bnw_core.bnw_objects as objs
from twisted.internet import defer


def _(s,user):
    return s


@defer.inlineCallbacks
def update_internal(message,what,delete,text):
    action = '$pull' if delete else '$addToSet'
    defer.returnValue((yield objs.Message.mupdate({'id':message},{action: { what: text}},safe=True)))

@check_arg(message=MESSAGE_COMMENT_RE)
@require_auth
@defer.inlineCallbacks
def cmd_update(request,message='',text='',club=False,tag=False,delete=False,raw=False):
    """ Редактирование сооббщений """
    message=canonic_message(message).upper()
    if not message or not ((text and (club or tag)) or raw):
        defer.returnValue(dict(
            ok=False,
            desc='Usage: <update|u> -m <message> <--club|--tag> '
                 '[--delete] [--raw] <tag|club>'))

    post=yield objs.Message.find_one({'id':message})

    if not post:
        defer.returnValue(
            dict(ok=False,desc='No such message.')
        )
    if post['user']!=request.user['name']:
        defer.returnValue(
            dict(ok=False,desc='Not your message.')
        )

    if raw:
        clubs = []
        tags = []
        for s in text.split(','):
            if len(s) > 1:
                if s.startswith("!"):
                    clubs.append(s[1:])
                    continue
                elif s.startswith("*"):
                    tags.append(s[1:])
                    continue
            defer.returnValue(dict(ok=False, desc='Wrong format.'))
        if len(clubs) > 5:
            defer.returnValue(dict(ok=False, desc='Too many clubs.'))
        if len(tags) > 5:
            defer.returnValue(dict(ok=False, desc='Too many tags.'))
        yield objs.Message.mupdate(
            {'id': message}, {'$set': {'clubs': clubs}}, safe=True)
        yield objs.Message.mupdate(
            {'id': message}, {'$set': {'tags': tags}}, safe=True)
        defer.returnValue(dict(ok=True, desc='Message updated.'))

    if club:
        if not delete and len(post['clubs'])>=5:
            defer.returnValue(
                dict(ok=False,desc='Too many clubs.')
            )
        _ = yield update_internal(message,'clubs',delete,text)
    if tag:
        if not delete and len(post['tags'])>=5:
            defer.returnValue(
                dict(ok=False,desc='Too many tags.')
            )
        _ = yield update_internal(message,'tags',delete,text)

    defer.returnValue(
        dict(ok=True,desc='Message updated.')
    )
