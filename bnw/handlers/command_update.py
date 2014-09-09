# -*- coding: utf-8 -*-
# from twisted.words.xish import domish

from base import *
import bnw.core.bnw_objects as objs
from twisted.internet import defer
from bnw.handlers import command_post


def _(s, user):
    return s


@defer.inlineCallbacks
def update_internal(message, what, delete, text):
    action = '$pull' if delete else '$addToSet'
    defer.returnValue((yield objs.Message.mupdate({'id': message}, {action: {what: text}})))


@defer.inlineCallbacks
def update_message_internal(request, message='', text='', club=False,
            tag=False, delete=False, clubs=None, tags=None, api=False,
            format=None):
    """Update message's clubs and tags."""
    message = canonic_message(message).upper()
    if (not message or not ((text and (club or tag)) or
                            (clubs is not None) or
                            (tags is not None) or api or format)):
        defer.returnValue(dict(
            ok=False,
            desc='Usage: <update|u> -m <message> <--club|--tag> '
                 '[--delete] <tag|club> [--clubs=club1,club2] '
                 '[--tags=tag1,tag2] '
                 '[--format=<markdown|md|moinmoin|mm|plaintext>]'))

    if format and not format in command_post.acceptable_formats:
        defer.returnValue(dict(ok=False, desc=u"'%s' is not a valid format! Choose one of: %s" % (format, command_post.acceptable_formats_str)))
    else:
        format = command_post.normalize_format(format)

    post = yield objs.Message.find_one({'id': message})

    if not post:
        defer.returnValue(
            dict(ok=False, desc='No such message.')
        )
    if post['user'] != request.user['name']:
        defer.returnValue(
            dict(ok=False, desc='Not your message.')
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
                {'id': message}, {'$set': {'clubs': clubs}})
        if tags is not None:
            tags = tags.split(',') if tags else []
            if filter(lambda s: not s, tags):
                defer.returnValue(dict(ok=False, desc='Wrong format.'))
            if len(tags) > 5:
                defer.returnValue(dict(ok=False, desc='Too many tags.'))
            yield objs.Message.mupdate(
                {'id': message}, {'$set': {'tags': tags}})
        defer.returnValue(dict(ok=True, desc='Message updated.'))

    if club:
        if not delete and len(post['clubs']) >= 5:
            defer.returnValue(
                dict(ok=False, desc='Too many clubs.')
            )
        _ = yield update_internal(message, 'clubs', delete, text)
    if tag:
        if not delete and len(post['tags']) >= 5:
            defer.returnValue(
                dict(ok=False, desc='Too many tags.')
            )
        _ = yield update_internal(message, 'tags', delete, text)

    if format:
        yield objs.Message.mupdate(
            {'id': message}, {'$set': {'format': format}})

    defer.returnValue(
        dict(ok=True, desc='Message updated.')
    )

@defer.inlineCallbacks
def update_comment_internal(request, comment='', text='', club=False,
            tag=False, delete=False, clubs=None, tags=None, api=False,
            format=None):
    """Update comment's format."""

    comment = canonic_message_comment(comment).upper()
    if not (comment and format):
        defer.returnValue(dict(
            ok = False,
            desc = u"Please specify a comment to update and a format to set."))

    if format and not format in command_post.acceptable_formats:
        defer.returnValue(dict(ok=False, desc=u"'%s' is not a valid format! Choose one of: %s" % (format, command_post.acceptable_formats_str)))
    else:
        format = command_post.normalize_format(format)

    if format:
        yield objs.Comment.mupdate(
            {'id': comment}, {'$set': {'format': format}})

    defer.returnValue(
        dict(ok=True, desc='Comment updated.')
    )

@check_arg(message=MESSAGE_COMMENT_RE)
@require_auth
@defer.inlineCallbacks
def cmd_update(request, message='', text='', club=False, tag=False,
               delete=False, clubs=None, tags=None, api=False, format=None):
    if message == MESSAGE_REC.match(message).group(0):
        # this is a message ID
        defer.returnValue((yield update_message_internal(request, message, text, club, tag, delete, clubs, tags, api, format)))
    elif message == MESSAGE_COMMENT_REC.match(message).group(0):
        # this is a comment ID
        defer.returnValue((yield update_comment_internal(request, message, text, club, tag, delete, clubs, tags, api, format)))
