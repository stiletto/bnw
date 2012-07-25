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
def cmd_update(request, message='', text='', club=False, tag=False,
               delete=False, clubs=None, tags=None, api=False):
    """Update message's clubs and tags."""
    message=canonic_message(message).upper()
    print repr(clubs), repr(tags)
    if (not message or not ((text and (club or tag)) or
                            (clubs is not None) or
                            (tags is not None) or api)):
        defer.returnValue(dict(
            ok=False,
            desc='Usage: <update|u> -m <message> <--club|--tag> '
                 '[--delete] <tag|club> [--clubs=club1,club2] '
                 '[--tags=tag1,tag2]'))

    post=yield objs.Message.find_one({'id':message})

    if not post:
        defer.returnValue(
            dict(ok=False,desc='No such message.')
        )
    if post['user']!=request.user['name']:
        defer.returnValue(
            dict(ok=False,desc='Not your message.')
        )

    if api:
        # Fucked tornado. It not save empty argument values in
        # self.request.arguments. Ugly workargound.
        # See https://
        # groups.google.com/forum/?fromgroups#!topic/python-tornado/PVP9NW_vFA0
        if not clubs:
            clubs = ''
        if not tags:
            tags = ''
    if clubs is not None or tags is not None:
        if clubs is not None:
            clubs = clubs.split(',') if clubs else []
            if filter(lambda s: not s, clubs):
                defer.returnValue(dict(ok=False, desc='Wrong format.'))
            if len(clubs) > 5:
                defer.returnValue(dict(ok=False, desc='Too many clubs.'))
            yield objs.Message.mupdate(
                {'id': message}, {'$set': {'clubs': clubs}}, safe=True)
        if tags is not None:
            tags = tags.split(',') if tags else []
            if filter(lambda s: not s, tags):
                defer.returnValue(dict(ok=False, desc='Wrong format.'))
            if len(tags) > 5:
                defer.returnValue(dict(ok=False, desc='Too many tags.'))
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
