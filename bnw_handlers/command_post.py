# -*- coding: utf-8 -*-

from base import *
import random
import time
from bnw_core.base import BnwResponse, get_webui_base
import bnw_core.bnw_objects as objs
from bnw_core.post import publish

from twisted.python import log
import bnw_core.post


def _(s, user):
    return s


@defer.inlineCallbacks
def throttle_check(user):
    post_throttle = yield objs.Throttle.find_one({'user': user})
    if post_throttle and post_throttle['time'] >= (time.time() - 5):
        raise BnwResponse('You are sending messages too fast!')
    defer.returnValue(post_throttle)


@defer.inlineCallbacks
def throttle_update(user, post_throttle):
        throttledoc = {'user': user, 'time': time.time()}
        if post_throttle:  # TODO: заменить на upsert
            _ = yield objs.Throttle.mupdate({'user': user}, throttledoc, safe=True)
        else:
            throttle = objs.Throttle(throttledoc)
            _ = yield throttle.save()
        defer.returnValue(None)


@defer.inlineCallbacks
def postMessage(request, tags, clubs, text, anon=False, anoncomments=False):
        post_throttle = yield throttle_check(request.user['name'])
        sfrom = request.to.userhost() if request.to else None
        start = text[:10].lower()
        if start.startswith('?otr'):
            defer.returnValue(
                dict(ok=False, desc='?OTR Error: Fuck your OTR, srsly')
            )
        ok, rest = yield bnw_core.post.postMessage(
            request.user, tags, clubs, text, anon, anoncomments, sfrom=sfrom)
        _ = yield throttle_update(request.user['name'], post_throttle)
        if ok:
            msgid, qn, recepients = rest
            defer.returnValue(
                dict(ok=True,
                     desc='Message #%s has been delivered '
                          'to %d users. %s/p/%s' % (
                     msgid, recepients, get_webui_base(request.user),
                     msgid),
                     id=msgid))
        else:
            defer.returnValue(
                dict(ok=False, desc=rest)
            )


@require_auth
@defer.inlineCallbacks
def cmd_post(request, tags="", clubs="", anonymous="", anoncomments="", text=""):
        """ Отправка псто """
        tags = tags.split(',')[:5]
        clubs = clubs.split(',')[:5]
        tags = filter(None, set(
            [x.lower().strip().replace('\n', ' ')[:256] for x in tags]))
        clubs = filter(None, set(
            [x.lower().strip().replace('\n', ' ')[:256] for x in clubs]))
        defer.returnValue(
            (yield postMessage(request, tags, clubs, text, anonymous, anoncomments)))


@defer.inlineCallbacks
def cmd_post_simple(request, text, tag1=None, tag2=None, tag3=None, tag4=None, tag5=None):
#        (ur'(?:(?P<tag1>[\*!]\S+)?(?: (?P<tag2>[\*!]\S+))?(?: (?P<tag3>[\*!]\S+))?(?: (?P<tag4>[\*!]\S+))?(?: (?P<tag5>[\*!]\S+))? )?(?P<text>.+)',
#            command_post.cmd_post_simple),
    """ Отправка псто """
    raw_tags = [t for t in (tag1, tag2, tag3, tag4, tag5) if t]
    clubs = ','.join([x[1:] for x in raw_tags if x.startswith('!')])
    tags = ','.join([x[1:] for x in raw_tags if x.startswith('*')])
    defer.returnValue((yield cmd_post(request, tags=tags, clubs=clubs, text=text)))


@require_auth
@check_arg(message=MESSAGE_COMMENT_RE)
@defer.inlineCallbacks
def cmd_comment(request, message="", anonymous="", text=""):
        """ Отправка комментария """
        message = canonic_message_comment(message).upper()
        message_id = message.split('/')[0]
        comment_id = message if '/' in message else None
        post_throttle = yield throttle_check(request.user['name'])
        sfrom = request.to.userhost() if request.to else None
        ok, rest = yield bnw_core.post.postComment(
            message_id, comment_id, text, request.user, anonymous, sfrom=sfrom)
        _ = yield throttle_update(request.user['name'], post_throttle)
        if ok:
            msgid, num, qn, recepients = rest
            defer.returnValue(
                dict(ok=True,
                     desc='Comment #%s (%d) has been delivered '
                          'to %d users. %s/p/%s' % (
                     msgid, num, recepients, get_webui_base(
                     request.user),
                     msgid.replace('/', '#')),
                     id=msgid,
                     num=num))
        else:
            defer.returnValue(
                dict(ok=False, desc=rest)
            )
        # log.debug


@require_auth
@check_arg(message=MESSAGE_RE)
@defer.inlineCallbacks
def cmd_recommend(request, message="", comment="", unrecommend=""):
        """Recommend or unrecommend message."""
        message_id = canonic_message(message).upper()
        message_obj = yield objs.Message.find_one({'id': message_id})
        if not message_obj:
            defer.returnValue(dict(
                ok=False,
                desc='No such message.'))
        if unrecommend:
            if request.user['name'] in message_obj['recommendations']:
                yield objs.Message.mupdate(
                    {'id': message_id},
                    {'$pull': {'recommendations': request.user['name']}})
                rcount = len(message_obj['recommendations']) - 1
                all_recos = list(message_obj['recommendations'])
                all_recos.remove(request.user['name'])
                publish('upd_recommendations_count',
                        message_id, rcount, all_recos)
                publish('upd_recommendations_count_in_' + message_id,
                        message_id, rcount, all_recos)
                defer.returnValue(dict(
                    ok=True,
                    desc='Message deleted from your recommendations list.'))
            else:
                defer.returnValue(dict(
                    ok=False,
                    desc='You haven\'t recommended this message.'))

        post_throttle = yield throttle_check(request.user['name'])
        ok, rest = yield bnw_core.post.recommendMessage(
            request.user, message_obj, comment)
        yield throttle_update(request.user['name'], post_throttle)
        if ok:
            qn, recepients, replies = rest
            defer.returnValue(dict(
                ok=True,
                desc='Recommended and delivered to %d users (%d replies).' % (
                    recepients, replies)))
        else:
            defer.returnValue(dict(
                ok=False,
                desc=rest))
