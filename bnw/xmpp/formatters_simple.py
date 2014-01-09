import datetime
from bnw_core.base import get_webui_base

formatters = {
    'comment': None,
    'message': None,
    'recommendation': None,
    'message_with_replies': None,
    'messages': None,
}


def format_message(request, msg, short=False):
    result = ('@%(author)s: %(tags)s %(clubs)s\n%(text)s\n' + ('\n' if not short else '') + '#%(id)s (%(rc)d) %(web)s/p/%(id)s') % \
        {'id': msg['id'].upper(),
         'author': msg['user'],
         'tags': ' '.join('*' + tag for tag in msg['tags']),
         'clubs': ' '.join('!' + tag for tag in msg['clubs']),
         'rc': msg['replycount'],
         'text': msg['text'],
         'web': get_webui_base(request.user),
         }
    return result


def format_comment(request, msg, short=False):
    args = {'id': msg['id'].split('/')[1].upper(),
            'author': msg['user'],
            'message': msg['message'].upper(),
            'replyto': msg['replyto'],
            'replytotext': msg['replytotext'],
            'rc': msg.get('num', -1),
            'text': msg['text'],
            'date': datetime.datetime.utcfromtimestamp(msg['date']).strftime('%d.%m.%Y %H:%M:%S'),
            'web': get_webui_base(request.user),
            }
    formatstring = ('' if short else 'Reply by ') + '@%(author)s:\n'
    if not short:
        formatstring += '>%(replytotext)s\n\n'
    formatstring += '%(text)s\n'
    if not short:
        formatstring += '\n'
    formatstring += '#%(message)s/%(id)s (%(rc)d)'
    if not short:
        formatstring += ' %(web)s/p/%(message)s#%(id)s'
    return formatstring % args


def formatter_messages(request, result):
    return 'Search results:\n' + '\n\n'.join((format_message(request, msg, True) for msg in result['messages']))


def formatter_message_with_replies(request, result):
    return format_message(request, result['message']) + '\n' + \
        '\n\n'.join(
        (format_comment(request, c, True) for c in result['replies']))


def formatter_subscriptions(request, result):
    return 'Your subscriptions:\n' + '\n'.join((s['type'][4:].ljust(5) + s['target'] for s in result['subscriptions']))


def formatter_message(request, result):
    return format_message(request, result['message'])


def formatter_recommendation(request, result):
    return 'Recommended by @%s: %s\n' % (result['recommender'], result['recocomment']) + \
        format_message(request, result['message'])


def formatter_comment(request, result):
    return format_comment(request, result['comment'])


def formatter_userlist(request, result):
    if not result['users']:
        return 'No more users.'
    return ' ' + ' '.join(
        '@' + u['name'].ljust(10) + ('\n' if i % 5 == 4 else '')
        for i, u in enumerate(result['users'])) + '\nuserlist ' + str(result['page'] + 1) + ' -- next page.'
