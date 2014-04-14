# -*- coding: utf-8 -*-
# from twisted.words.xish import domish

from base import *
import bnw.core.bnw_objects as objs


def _(s, user):
    return s


def update_internal(message, what, delete, text):
    action = '$pull' if delete else '$addToSet'
    return objs.Message.mupdate({'id': message}, {action: {what: text}})


@check_arg(message=MESSAGE_COMMENT_RE)
@require_auth
def cmd_update(request, message='', text='', club=False, tag=False,
               delete=False, clubs=None, tags=None, api=False):
    """Update message's clubs and tags."""
    message = canonic_message(message).upper()
    if (not message or not ((text and (club or tag)) or
                            (clubs is not None) or
                            (tags is not None) or api)):
        return dict(
            ok=False,
            desc='Usage: <update|u> -m <message> <--club|--tag> '
                 '[--delete] <tag|club> [--clubs=club1,club2] '
                 '[--tags=tag1,tag2]')

    post = objs.Message.find_one({'id': message})

    if not post:
        return dict(ok=False, desc='No such message.')
    if post['user'] != request.user['name']:
        return dict(ok=False, desc='Not your message.')

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
                return dict(ok=False, desc='Wrong format.')
            if len(clubs) > 5:
                return dict(ok=False, desc='Too many clubs.')
            objs.Message.mupdate(
                {'id': message}, {'$set': {'clubs': clubs}})
        if tags is not None:
            tags = tags.split(',') if tags else []
            if filter(lambda s: not s, tags):
                return dict(ok=False, desc='Wrong format.')
            if len(tags) > 5:
                return dict(ok=False, desc='Too many tags.')
            objs.Message.mupdate(
                {'id': message}, {'$set': {'tags': tags}})
        return dict(ok=True, desc='Message updated.')

    if club:
        if not delete and len(post['clubs']) >= 5:
            return dict(ok=False, desc='Too many clubs.')
        update_internal(message, 'clubs', delete, text)
    if tag:
        if not delete and len(post['tags']) >= 5:
            return dict(ok=False, desc='Too many tags.')
        update_internal(message, 'tags', delete, text)

    return dict(ok=True, desc='Message updated.')
