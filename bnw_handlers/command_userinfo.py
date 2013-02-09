from twisted.internet import defer

import bnw_core.bnw_objects as objs


@defer.inlineCallbacks
def cmd_userinfo(request, user=''):
    if not user:
        defer.returnValue(dict(ok=False, desc='Username required.'))
    user_obj = yield objs.User.find_one({'name': user})
    subscribers = yield objs.Subscription.find(dict(
        target=user, type='sub_user'))
    subscribers = set([x['user'] for x in subscribers])
    subscriptions = yield objs.Subscription.find(dict(
        user=user, type='sub_user'))
    subscriptions = set([x['target'] for x in subscriptions])
    friends = list(subscribers & subscriptions)
    friends.sort()
    subscribers_only = list(subscribers - subscriptions)
    subscribers_only.sort()
    subscriptions_only = list(subscriptions - subscribers)
    subscriptions_only.sort()
    messages_count = int((yield objs.Message.count({'user': user})))
    comments_count = int((yield objs.Comment.count({'user': user})))
    vcard = user_obj.get('vcard', {})
    about = user_obj.get('settings', {}).get('about', '')
    if not about:
        about = vcard.get('desc', '')
    defer.returnValue({
        'user': user,
        'regdate': user_obj.get('regdate', 0),
        'messages_count': messages_count,
        'comments_count': comments_count,
        'subscribers': subscribers_only,
        'subscriptions': subscriptions_only,
        'friends': friends,
        'vcard': vcard,
        'about': about,
    })
