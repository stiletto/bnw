from twisted.internet import defer

from bnw.handlers.base import canonic_user
import bnw.core.bnw_objects as objs


@defer.inlineCallbacks
def cmd_userinfo(request, user=''):
    # DB interactions
    if not user:
        defer.returnValue(dict(ok=False, desc='Username required.'))
    user = canonic_user(user)
    user_obj = yield objs.User.find_one({'name': user})
    if not user_obj:
        defer.returnValue(dict(ok=False, desc='User not found.'))
    subscribers = yield objs.Subscription.find(dict(
        target=user, type='sub_user'))
    subscribers = set([x['user'] for x in subscribers])
    subscriptions = yield objs.Subscription.find(dict(
        user=user, type='sub_user'))
    subscriptions = set([x['target'] for x in subscriptions])
    messages_count = int((yield objs.Message.count({'user': user})))
    comments_count = int((yield objs.Comment.count({'user': user})))
    characters_stat = yield objs.StatCharacters.find_one({'_id': user})
    characters_count = int(characters_stat['value']) if characters_stat else 0

    # Data processing
    subscribers_all = list(subscribers)
    subscribers_all.sort()
    subscriptions_all = list(subscriptions)
    subscriptions_all.sort()
    friends = list(subscribers & subscriptions)
    friends.sort()
    subscribers_only = list(subscribers - subscriptions)
    subscribers_only.sort()
    subscriptions_only = list(subscriptions - subscribers)
    subscriptions_only.sort()
    vcard = user_obj.get('vcard', {})
    about = user_obj.get('settings', {}).get('about', '')
    if not about:
        about = vcard.get('desc', '')

    # Result
    defer.returnValue({
        'ok': True,
        'user': user,
        'regdate': user_obj.get('regdate', 0),
        'messages_count': messages_count,
        'comments_count': comments_count,
        'characters_count': characters_count,
        'subscribers': subscribers_only,
        'subscribers_all': subscribers_all,
        'subscriptions': subscriptions_only,
        'subscriptions_all': subscriptions_all,
        'friends': friends,
        'vcard': vcard,
        'about': about,
        'loltroll': user_obj.get('loltroll', None),
    })
