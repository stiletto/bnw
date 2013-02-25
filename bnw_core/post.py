# coding: utf-8
"""
"""
import bnw_objects as objs
from base import genid, cropstring, get_webui_base
from bnw_mongo import mongo_errors
from twisted.internet import defer, reactor
import time
from twisted.python import log

listeners = {}


@defer.inlineCallbacks
def subscribe(user, target_type, target, fast=False, sfrom=None):
    """!Подписка пользователя на что-нибудь.
    @param user Объект-пользователь.
    @param target_type Тип цели - user,tag,club.
    @param target Цель подписки.
    @param fast Если равно true, не проверяем существование подписки."""
    sub_rec = {'user': user['name'], 'target': target, 'type': target_type}
    adddesc = ''
    if fast or ((yield objs.Subscription.find_one(sub_rec)) is None):
        sub = objs.Subscription(sub_rec)
        sub['jid'] = user['jid']
        if sfrom:
            sub['from'] = sfrom
        if target_type == 'sub_user':
            tuser = yield objs.User.find_one({'name': target})
            if not tuser:
                defer.returnValue((False, 'No such user.'))
            _ = yield tuser.send_plain(
                '@%s subscribed to your blog. %s/u/%s' % (
                    user['name'], get_webui_base(tuser), user['name']))
            pass
        elif target_type == 'sub_message':
            if not fast:
                msg = yield objs.Message.find_one({'id': target})
                if not msg:
                    defer.returnValue((False, 'No such message.'))
                else:
                    adddesc = ' (%d replies)' % (msg['replycount'],)

            feedel_val = dict(user=user['name'], message=target)
            feedel = None if fast else (yield objs.FeedElement.find_one(feedel_val))
            if not feedel:
                feedel_val.update(dict(recommender=None,
                                       recocomment=None,
                                       date=time.time()))
                feedel = objs.FeedElement(feedel_val)
                _ = yield feedel.save()
        if (yield sub.save()):
            defer.returnValue((True, 'Subscribed' + adddesc + '.'))
        else:
            defer.returnValue((False, 'Error while saving.'))
    else:
        defer.returnValue((False, 'Already subscribed.'))


@defer.inlineCallbacks
def unsubscribe(user, target_type, target, fast=False):
    """!Отписка пользователя от чего-нибудь.
    @param user Объект-пользователь.
    @param target_type Тип цели - user,tag,club.
    @param target Цель подписки.
    @param fast Игнорируется."""
    sub_rec = {'user': user['name'], 'target': target, 'type': target_type}
    rest = yield objs.Subscription.remove(sub_rec)
    defer.returnValue((True, 'Unsubscribed.'))


def isdisjoint_compat(self, other):
    for value in other:
        if value in self:
            return False
    return True

if not hasattr(frozenset, "isdisjoint"):
    isdisjoint = isdisjoint_compat
else:
    isdisjoint = frozenset.isdisjoint


@defer.inlineCallbacks
def send_to_subscribers(queries, message, recommender=None, recocomment=None):
    """!Это дерьмо рассылает сообщение или коммент подписчикам.
    @param queries Список запросов, по которым можно найти подписки.
    @param is_message Является ли сообщением. Если нет - коммент.
    @param message Собственно сообщение или коммент.
    @todo Что-то как-то уныло и негибко.
    @todo Эта функция давно плачет ночами о хоть одной сучилище, которая её бы отрефакторила
    """
    recipients = {}
    qn = 0
    for query in queries:
        qn += 1
        for result in (yield objs.Subscription.find(query, fields=['user', 'from'])):
            if result['user'] == message['user'] or result['user'] == message.get('real_user'):
                continue
            recipients[result['user']] = result
    reccount = 0
    bl_items = frozenset([('user', message['user'])] + [('tag', x) for x in message.get('tags', [])] +
                         [('club', x) for x in message.get('clubs', [])])

    for target_name, subscription in recipients.iteritems():
        target = yield objs.User.find_one({'name': target_name})
        qn += 1
        if target:
            if isdisjoint(bl_items, (tuple(x) for x in target.get('blacklist', []))):
                reccount += yield message.deliver(target, recommender, recocomment, sfrom=subscription.get('from', None))
                log.msg('Sent %s to %s' % (message['id'], target['jid']))
            else:
                log.msg('Not delivering %s to %s because of blacklist' % (
                    message['id'], target['jid']))
    defer.returnValue((qn, reccount))


@defer.inlineCallbacks
def postMessage(user, tags, clubs, text, anon=False, anoncomments=False, sfrom=None):
    """!Это дерьмо создает новое сообщение и рассылает его.
    @param user Объект-пользователь.
    @param tags Список тегов.
    @param clubs Список клубов.
    @param text Текст сообщения.
    @param anon Отправить от анона.
    @param anoncom Все комментарии принудительно анонимны.
    """
    if len(text) == 0:
        defer.returnValue((False, 'So where is your post?'))
    if len(text) > 10240:
        defer.returnValue(
            (False, 'Message is too long. %d/10240' % (len(text),)))
    message = {'user': user['name'],
               'tags': tags,
               'clubs': clubs,
               'id': genid(6),
               'date': time.time(),
               'replycount': 0,
               'text': text,
               'anonymous': bool(anon),
               'anoncomments': bool(anoncomments),
               'recommendations': [],
               }
    if anon:
        message['real_user'] = message['user']
        message['user'] = 'anonymous'
    stored_message = objs.Message(message)
    stored_message_id = yield stored_message.save()

    sub_result = yield subscribe(user, 'sub_message', message['id'], True, sfrom)

    queries = [{'target': tag, 'type': 'sub_tag'} for tag in tags]
    queries += [{'target': club, 'type': 'sub_club'} for club in clubs]
    if ('@' in clubs) or (len(clubs) == 0):
        queries += [{'target': 'anonymous' if anon else user[
            'name'], 'type': 'sub_user'}]
    qn, recipients = yield send_to_subscribers(queries, stored_message)
    filtered = stored_message.filter_fields()
    publish('new_message', filtered)  # ALARM
    publish('new_message_on_user_' + message['user'], filtered)
    defer.returnValue((True, (message['id'], qn, recipients)))


@defer.inlineCallbacks
def postComment(message_id, comment_id, text, user, anon=False, sfrom=None):
    """!Это дерьмо постит комментарий.
    @param message_id Id сообщения к которому комментарий.
    @param comment_id Если ответ - id комментария, на который отвечаем.
    @param text Текст комментария.
    @param user Объект-пользователь.
    @param anon Анонимный ответ.
    """

    if len(text) == 0:
        defer.returnValue((False, 'So where is your comment?'))
    if len(text) > 4096:
        defer.returnValue(
            (False, 'Comment is too long. %d/4096' % (len(text),)))
    message = yield objs.Message.find_one({'id': message_id})
    if comment_id:
        old_comment = yield objs.Comment.find_one({'id': comment_id, 'message': message_id})
    else:
        old_comment = None
    if (not old_comment) and comment_id:
        defer.returnValue((False, 'No such comment.'))
    if not message:
        defer.returnValue((False, 'No such message.'))
    if message.get('anoncomments'):
        anon = True

    comment = {'user': user['name'],
               'message': message_id,
               'date': time.time(),
               'replyto': old_comment['id'] if old_comment else None,
               'num': message['replycount'] + 1,
               'replytotext': cropstring(old_comment['text'] if comment_id else message['text'], 128),
               'text': ('@' + old_comment['user'] + ' 'if comment_id else '') + text,
               'anonymous': bool(anon),
               }
#              'depth': old_comment.get('depth',0)+1 if old_comment else 0,
    if anon:
        comment['real_user'] = comment['user']
        comment['user'] = 'anonymous'
    comment = objs.Comment(comment)
    for x in range(0, 10):
        try:
            comment['id'] = message_id + '/' + genid(3)
            comment_id = yield comment.save()
        except mongo_errors.OperationFailure, e:
            pass
            # if e['code']!=11000:
            #    raise
        else:
            break
    else:
        defer.returnValue(
            (False, 'Looks like this message has reached its bumplimit.'))
    sub_result = yield subscribe(user, 'sub_message', message_id, False, sfrom)
    _ = (yield objs.Message.mupdate({'id': message_id}, {'$inc': {'replycount': 1}}))

    qn, recipients = yield send_to_subscribers([{'target': message_id, 'type': 'sub_message'}], comment)
    publish('new_comment_in_' + message_id, comment.filter_fields())  # ALARM
    publish('upd_comments_count', message_id, comment['num'])
    defer.returnValue((True, (comment['id'], comment['num'], qn, recipients)))


@defer.inlineCallbacks
def recommendMessage(user, message, comment="", sfrom=None):
    """Add message to user's recommendations list and send it to subscribers.
    @param user User object.
    @param message Message object.
    @param comment Recommendation comment (optional).
    """
    if not comment:
        comment = ""
    if len(comment) > 256:
        defer.returnValue(
            (False, 'Recommendation is too long. %d/256' % len(comment)))

    # TODO: Message will be queried once more by its id.
    sub_result = yield subscribe(
        user, 'sub_message', message['id'], False, sfrom)

    queries = [{'target': user['name'], 'type': 'sub_user'}]
    qn, recipients = yield send_to_subscribers(
        queries, message, user['name'], comment)

    if user['name'] != message['user']:
        tuser = yield objs.User.find_one({'name': message['user']})
        yield tuser.send_plain(
            '@%s recommended your message #%s, '
            'so %d more users received it. %s/p/%s' % (
                user['name'], message['id'], recipients,
                get_webui_base(tuser), message['id']))
        recos_count = len(message['recommendations'])
        if (recos_count < 1024 and
                user['name'] not in message['recommendations']):
                yield objs.Message.mupdate(
                    {'id': message['id']},
                    {'$addToSet': {'recommendations': user['name']}})
                all_recos = message['recommendations'] + [user['name']]
                publish('upd_recommendations_count', message['id'],
                        recos_count + 1, all_recos)

    defer.returnValue((True, (qn, recipients, message['replycount'])))

listenerscount = 0


def register_listener(etype, name, handler):
    global listeners
    global listenerscount
    listenerscount += 1
    if not (etype in listeners):
        listeners[etype] = {}
    listeners[etype][name] = handler


def unregister_listener(etype, name):
    global listeners
    global listenerscount
    listenerscount -= 1
    del listeners[etype][name]
    if not listeners[etype]:
        del listeners[etype]


def publish(etype, *args, **kwargs):
    global listeners
    for rtype in (etype, None):
        if rtype in listeners:
            for listener in listeners[rtype].itervalues():
                reactor.callLater(0, listener, *args, **kwargs)
