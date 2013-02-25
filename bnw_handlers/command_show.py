# coding: utf-8

import time

import pymongo

from base import *
import bnw_core.bnw_objects as objs


@defer.inlineCallbacks
def showSearch(parameters, page, auth_user=None):
    # FIXME: THIS COMMAND IS FUCKING SLOW SLOW SLOW AND WAS WRITTEN BY A
    # BRAIN-DAMAGED IDIOT
    messages=[x.filter_fields() for x in  (yield objs.Message.find_sort(
        parameters,[('date',pymongo.DESCENDING)],limit=20,skip=page*20))]
    # Get subscriptions info
    if auth_user is not None:
        ids = [m['id'] for m in messages]
        subscriptions = yield objs.Subscription.find({
            'user': auth_user, 'type': 'sub_message', 'target': {'$in': ids}})
        sub_ids = [s['target'] for s in subscriptions]
        for msg in messages:
            msg['subscribed'] = True if msg['id'] in sub_ids else False
    messages.reverse()
    defer.returnValue(dict(
        ok=True, format="messages", cache=5, cache_public=True,
        messages=messages))


@defer.inlineCallbacks
def showComment(commentid):
        comment=yield objs.Comment.find_one({'id': commentid})
        if comment is None:
            defer.returnValue(
                dict(ok=False,desc='No such comment',cache=5,cache_public=True)
            )
        defer.returnValue(
            dict(ok=True,format='comment', cache=5, cache_public=True,
                comment=comment.filter_fields(),
                    ))


@defer.inlineCallbacks
def showComments(msgid, auth_user=None):
        message=yield objs.Message.find_one({'id': msgid})
        if message is None:
            defer.returnValue(
                dict(ok=False,desc='No such message',cache=5,cache_public=True)
            )
        if auth_user is not None:
            subscribed = yield objs.Subscription.count({
                'user': auth_user, 'type': 'sub_message', 'target': msgid})
            message['subscribed'] = bool(subscribed)
        defer.returnValue(dict(
            ok=True, format='message_with_replies', cache=5, cache_public=True,
            msgid=msgid, message=message.filter_fields(),
            replies=[comment.filter_fields() for comment in (
                yield objs.Comment.find_sort(
                    {'message': msgid.upper()},[('date',pymongo.ASCENDING)]))
            ]))


@check_arg(message=MESSAGE_COMMENT_RE, page='[0-9]+')
@defer.inlineCallbacks
def cmd_show(request, message='', user='', tag='', club='', page='0',
             show='messages', replies=None):
    """Show messages by specified parameters."""
    message = canonic_message_comment(message).upper()
    auth_user = request.user['name'] if request.user else None
    if '/' in message:
        defer.returnValue((yield showComment(message)))
    if replies:
        if not message:
            defer.returnValue(dict(
                ok=False,
                desc="Error: 'replies' is allowed only with 'message'.",
                cache=3600))
        defer.returnValue((yield showComments(message, auth_user)))
    else:
        if show not in ['messages', 'recommendations', 'all']:
            defer.returnValue(dict(
                ok=False, desc="Bad 'show' parameter value."))
        parameters = [('tags', tag), ('clubs', club), ('id', message.upper())]
        parameters = dict(p for p in parameters if p[1])
        if user:
            user = user.lower()
            if show == 'messages':
                user_spec = dict(user=user)
            elif show == 'recommendations':
                user_spec = dict(recommendations=user)
            else:
                user_spec = {'$or': [{'user': user}, {'recommendations': user}]}
            parameters.update(user_spec)
        defer.returnValue((yield showSearch(parameters, int(page), auth_user)))


@require_auth
@defer.inlineCallbacks
def cmd_feed(request,page="0"):
    """ Показать ленту """
    page=int(page) if page else 0
    feed = yield objs.FeedElement.find_sort({'user':request.user['name']},
                                [('_id',pymongo.DESCENDING)],limit=20,skip=page*20)
    messages = [x.filter_fields() for x in (yield objs.Message.find_sort({'id': { '$in': 
            [f['message'] for f in feed]
        }},[('date',pymongo.ASCENDING)]))]
    defer.returnValue(
        dict(ok=True,format="messages",
             messages=messages,
             desc='Your feed',
             cache=5)
    )


TODAY_REBUILD_PERIOD = 300
TODAY_MAP = 'function() { emit(this.message, 1); }'
TODAY_REDUCE = 'function(k,vals) { var sum=0; for(var i in vals) sum += vals[i]; return sum; }'


@defer.inlineCallbacks
def cmd_today(request):
    """ Показать обсуждаемое за последние 24 часа """
    last_rebuild = yield objs.GlobalState.find_one({'name':'today_rebuild'})
    if not last_rebuild:
        last_rebuild = {'name':'today_rebuild','value':0}
    rebuild = time.time() > TODAY_REBUILD_PERIOD + last_rebuild['value']
    if rebuild:
        _ = yield objs.GlobalState.mupdate({'name':'today_rebuild'},{'name':'today_rebuild','value':time.time()},True)
        
        start = time.time() - 86400
        _ = yield objs.Today.remove({})
        result = yield objs.Comment.map_reduce(TODAY_MAP,TODAY_REDUCE,out='today',query={'date':{'$gte':start}})
    if (not rebuild) or result:
        postids = list(x['_id'] for x in (yield objs.Today.find_sort({},[('value',-1)],limit=20)))
        dbposts = dict((x['id'],x.filter_fields()) for x in (yield objs.Message.find({'id':{'$in':postids}})))
        messages = [dbposts[x] for x in postids if (x in dbposts)]
        messages.reverse()
        defer.returnValue(
            dict(ok=True,format="messages",
                 messages=messages,
                 desc='Today''s most discussed',
                 cache=300)
        )
    else:
        defer.returnValue(dict(ok=False,desc='Map/Reduce failed'))


@defer.inlineCallbacks
def cmd_today2(request):
    """ Показать обсуждаемое за последние 24 часа """
    start = time.time() - 86400
    messages = [x.filter_fields() for x in (yield objs.Message.find_sort({'date':{'$gte':start}},[('replycount',pymongo.DESCENDING)],limit=20))]
    messages.reverse()
    defer.returnValue(
        dict(ok=True,format="messages",
             messages=messages,
             desc='Today''s most discussed',
             cache=300)
    )
