import datetime
from bnw_core.base import get_webui_base

formatters = {
    'comment': None,
    'message': None,
    'recommendation': None,
    'message_with_replies': None,
    'messages': None,
}

def format_message(request,msg):
    result = '+++ [%s] %s:\n' % (
        datetime.datetime.utcfromtimestamp(msg['date']).strftime('%d.%m.%Y %H:%M:%S'),
        msg['user'],)
    if msg['tags']:
        result += 'Tags: %s\n' % (', '.join(msg['tags']),)
    if msg['clubs']:
        result += 'Clubs: %s\n' % (', '.join(msg['clubs']),)
    result += '\n%s\n' % (msg['text'],)
    result += '--- %(id)s (%(rc)d) %(base_url)s/p/%(id)s' % {
               'base_url': get_webui_base(request.user),
               'id': msg['id'].upper(),
               'rc':    msg['replycount'],
             }
    return result
    
def format_comment(request,msg,short=False):
    args = { 'id':    msg['id'].split('/')[1].upper(),
             'author':msg['user'],
             'message':msg['message'].upper(),
             'replyto':None if msg['replyto'] is None else msg['replyto'].upper(),
             'replytotext': msg['replytotext'],
             'text':  msg['text'],
             'num':   msg.get('num',-1),
             'date':  datetime.datetime.utcfromtimestamp(msg['date']).strftime('%d.%m.%Y %H:%M:%S'),
             'web': get_webui_base(request.user),
           }
    formatstring = '+++ [ %(date)s ] %(author)s'
    if msg['replyto']:
        formatstring += ' (in reply to %(replyto)s):\n'
    else:
        formatstring += ' (in reply to %(message)s):\n'
    if not short:
        formatstring += '>%(replytotext)s\n'
    formatstring += '\n%(text)s\n--- %(message)s/%(id)s (%(num)d) %(web)s/p/%(message)s#%(id)s'
    return formatstring % args

def formatter_messages(request,result):
    return 'Search results:\n'+'\n'.join((format_message(request,msg) for msg in result['messages']))

def formatter_message_with_replies(request,result):
    return format_message(request,result['message']) + '\n' + \
            '\n'.join((format_comment(request,c,True) for c in result['replies']))

def formatter_search(request, result):
    total, results = result['search_result']
    if not results:
        return 'No results found.'
    info = 'Found %d results' % total
    if total > 10:
        info += ' (displaying first 10)'
    print repr(info)
    out = [info+':']
    for res in results:
        out.append('@%s: %s (%s%%)\n%s\n\n#%s %s/p/%s' % (
            res['user'], res['tags_info'], res['percent'], res['text'],
            res['id'], get_webui_base(request.user),
            res['id'].replace('/', '#')))
    return '\n\n'.join(out)

def formatter_subscriptions(request,result):
    return 'Your subscriptions:\n'+'\n'.join(
        (s['type'][4:].ljust(5)+s['target'].rjust(10)+' '+s.get('from','')
         for s in result['subscriptions']))

def formatter_blacklist(request,result):
    return 'Your blacklist:\n'+'\n'.join(
        (s[0].ljust(5)+s[1].rjust(10)
         for s in result['blacklist']))

def formatter_message(request,result):
    return '\n'+format_message(request,result['message'])

def formatter_recommendation(request,result):
    return '\nRecommended by @%s: %s\n' % (result['recommender'],result['recocomment']) + \
        format_message(request,result['message'])

def formatter_comment(request,result):
    return '\n'+format_comment(request,result['comment'])

def formatter_userlist(request,result):
    if not result['users']:
        return 'No more users.'
    return ' '+' '.join(
        '@'+u['name'].ljust(10)+('\n' if i%5==4 else '')
            for i,u in enumerate(result['users']))+'\nuserlist -p '+str(result['page']+1)+' -- next page.'

def formatter_settings(request,result):
    return ('Currrent settings:\n' +
        '\n'.join('%s\t%s' % (k,v) for k,v in result['settings'].iteritems()))

def formatter_clubs(request,result):
    return ' '+' '.join(
        ''+u['_id'].ljust(15)+' '+str(int(u['value'])).ljust(3)+('\n' if i%5==4 else '')
            for i,u in enumerate(result['clubs']))

def formatter_jids(request,result):
    res = 'JIDs:\n' + ' '.join(u for u in result['jids'])
    if result['pending_jids']:
        res += '\n\nPending JIDs:\n' + ' '.join(u for u in result['pending_jids'])
    res += '\n\nActive JID: ' + result['jid']
    return res
