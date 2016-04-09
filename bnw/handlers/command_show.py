# coding: utf-8

import time

import pymongo

from base import *
import bnw.core.bnw_objects as objs


def get_user_bl(request, use_bl=False):
    """Return authed user blacklist or simply an empty list
    if user not authed.

    :param use_bl: default False. Whether we should return actual
                   blacklist or just empty list.
    """
    if use_bl and request.user:
        bl = request.user.get('blacklist', [])
        bl = [el[1] for el in bl if el[0] == 'user']
        return bl
    else:
        return []


@defer.inlineCallbacks
def set_subscriptions_info(request, messages):
    """Add 'subscribed' param for each message which
    indicate do the user subscribed on the message or not.
    Return updated list of messages (update in place actually!).
    For non-authed users return non-modified list.

    :param request: BnW request object.
    """
    if not request.user:
        defer.returnValue(messages)

    user = request.user['name']
    ids = [m['id'] for m in messages]
    subscriptions = yield objs.Subscription.find({
        'user': user, 'type': 'sub_message', 'target': {'$in': ids}})
    sub_ids = [s['target'] for s in subscriptions]
    for msg in messages:
        msg['subscribed'] = True if msg['id'] in sub_ids else False
    defer.returnValue(messages)

def replace_banned(regions, message, kind='message'):
    banned_regions = regions.intersection(set(message.get('banned_in', [])))
    if len(banned_regions) > 0:
        banmsg = 'This %s is banned in regions: %s' % (kind, ','.join(banned_regions))
        message['banned'] = True
        message['text'] = '**'+banmsg+'**'
        banhtml = '''<span style='color: #f00;'>'''+banmsg+'</span>'
        message['html'] = { 'secure': [banhtml, []], 'insecure': [banhtml, []] }
    return message


@defer.inlineCallbacks
def showSearch(parameters, page, request):
    messages = [x.filter_fields() for x in (yield objs.Message.find_sort(
        parameters, [('date', pymongo.DESCENDING)], limit=20, skip=page * 20))]
    messages = yield set_subscriptions_info(request, messages)
    regions = request.regions
    for message in messages:
        replace_banned(regions, message)
    messages.reverse()
    defer.returnValue(dict(
        ok=True, format="messages", cache=5, cache_public=True,
        messages=messages))


@defer.inlineCallbacks
def showComment(commentid, request):
        comment = yield objs.Comment.find_one({'id': commentid})
        if comment is None:
            defer.returnValue(
                dict(ok=False, desc='No such comment',
                     cache=5, cache_public=True)
            )
        replace_banned(request.regions, comment, 'comment')
        defer.returnValue(
            dict(ok=True, format='comment', cache=5, cache_public=True,
                         comment=comment.filter_fields(),
                 ))


@defer.inlineCallbacks
def showComments(msgid, request, bl=None, after=''):
    message = yield objs.Message.find_one({'id': msgid})
    if message is None:
        defer.returnValue(dict(
            ok=False, desc='No such message', cache=5, cache_public=True))
    if request.user:
        user = request.user['name']
        subscribed = yield objs.Subscription.count({
            'user': user, 'type': 'sub_message', 'target': msgid})
        message['subscribed'] = bool(subscribed)
    qdict = {'message': msgid.upper()}
    if bl:
        qdict['user'] = {'$nin': bl}
    if after:
        after_comment = yield objs.Comment.find_one({'id':msgid+'/'+after.split('/')[-1]})
        if after_comment:
            qdict['date'] = {'$gte': after_comment['date']}
    regions = request.regions
    replace_banned(regions, message)
    comments = yield objs.Comment.find_sort(
        qdict, [('date', pymongo.ASCENDING)], limit=10000)
    for comment in comments:
        replace_banned(regions, comment, 'comment')
    defer.returnValue(dict(
        ok=True, format='message_with_replies', cache=5, cache_public=True,
        msgid=msgid, message=message.filter_fields(),
        replies=[comment.filter_fields() for comment in comments]))


@check_arg(message=MESSAGE_COMMENT_RE, page='[0-9]+')
@defer.inlineCallbacks
def cmd_show(request, message='', user='', tag='', club='', page='0',
             show='messages', replies=None, use_bl=False, after='', before=''):
    """Show messages by specified parameters."""
    message = canonic_message_comment(message).upper()
    bl = get_user_bl(request, use_bl)
    if '/' in message:
        defer.returnValue((yield showComment(message, request)))
    if replies:
        if not message:
            defer.returnValue(dict(
                ok=False,
                desc="Error: 'replies' is allowed only with 'message'.",
                cache=3600))
        defer.returnValue((yield showComments(message, request, bl, after)))
    else:
        if show not in ['messages', 'recommendations', 'all']:
            defer.returnValue(dict(
                ok=False, desc="Bad 'show' parameter value."))
        parameters = [('tags', tag), ('clubs', club), ('id', message.upper())]
        parameters = dict(p for p in parameters if p[1])
        if user:
            user = canonic_user(user).lower()
            if show == 'messages':
                user_spec = dict(user=user)
            elif show == 'recommendations':
                user_spec = dict(recommendations=user)
            else:
                user_spec = {'$or': [{'user': user}, {
                    'recommendations': user}]}
            parameters.update(user_spec)
        elif bl:
            parameters['user'] = {'$nin': bl}

        if before:
            befmsg = yield objs.Message.find_one({'id': before})
            if befmsg:
                parameters['date'] = {'$lt': befmsg['date']}
            else:
                defer.returnValue(dict(ok=False, desc="Message to search before doesn't exist."))

        if after:
            afmsg = yield objs.Message.find_one({'id': after})
            if afmsg:
                parameters['date'] = {'$gt': afmsg['date']}
            else:
                defer.returnValue(dict(ok=False, desc="Message to search after doesn't exist."))
        defer.returnValue((yield showSearch(parameters, int(page), request)))


@require_auth
@defer.inlineCallbacks
def cmd_feed(request, page="0"):
    """ Показать ленту """
    page = int(page) if page else 0
    feed = yield objs.FeedElement.find_sort({'user': request.user['name']},
                                            [('_id', pymongo.DESCENDING)], limit=20, skip=page * 20)
    messages = [x.filter_fields() for x in (yield objs.Message.find_sort({'id': {'$in':
                                                                                 [f['message']
                                                                                     for f in feed]
                                                                                 }}, [('date', pymongo.ASCENDING)]))]
    regions = request.regions
    for message in messages:
        replace_banned(regions, message)
    defer.returnValue(
        dict(ok=True, format="messages",
             messages=messages,
             desc='Your feed',
             cache=5)
    )


@defer.inlineCallbacks
def cmd_today(request, use_bl=False):
    """ Показать обсуждаемое за последние 24 часа """
    bl = get_user_bl(request, use_bl)

    for x in range(10):
        postids = [x['_id'] for x in (yield objs.Today.find({}, limit=20))]
        if len(postids)>0: break
    qdict = {'id': {'$in': postids}}
    if bl: qdict['user'] = {'$nin': bl}
    dbposts = dict(
        (x['id'], x.filter_fields())
        for x in (yield objs.Message.find(qdict)))
    messages = [dbposts[x] for x in postids if (x in dbposts)]
    regions = request.regions
    for message in messages:
        replace_banned(regions, message)
    messages = yield set_subscriptions_info(request, messages)
    messages.reverse()
    defer.returnValue(
        dict(ok=True, format="messages",
             messages=messages,
             desc='Today''s most discussed',
             cache=300)
    )


@defer.inlineCallbacks
def cmd_today2(request):
    """ Показать обсуждаемое за последние 24 часа """
    start = time.time() - 86400
    messages = [x.filter_fields() for x in (yield objs.Message.find_sort({'date': {'$gte': start}}, [('replycount', pymongo.DESCENDING)], limit=20))]
    messages.reverse()
    defer.returnValue(
        dict(ok=True, format="messages",
             messages=messages,
             desc='Today''s most discussed',
             cache=300)
    )
