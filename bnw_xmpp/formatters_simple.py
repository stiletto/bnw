# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

import random
import datetime
import bnw_core.base
gc = bnw_core.base.gc

formatters = {
    'comment': None,
    'message': None,
    'recommendation': None,
    'message_with_replies': None,
    'messages': None,
}

def format_message(msg,short=False):
    result=('@%(author)s: %(tags)s %(clubs)s\n%(text)s\n'+('\n' if not short else '')+'#%(id)s (%(rc)d) %(web)sp/%(id)s') % \
           { 'id':    msg['id'].upper(),
             'author':msg['user'],
             'tags':  ' '.join('*'+tag for tag in msg['tags']),
             'clubs': ' '.join('!'+tag for tag in msg['clubs']),
             'rc':    msg['replycount'],
             'text':  msg['text'],
             'web': gc('webui_base'),
           }
    return result
    
def format_comment(msg,short=False):
    args={    'id':    msg['id'].split('/')[1].upper(),
              'author':msg['user'],
              'message':msg['message'].upper(),
              'replyto': msg['replyto'],
              'replytotext': msg['replytotext'],
              'rc':    msg.get('num',-1),
              'text':  msg['text'],
              'date':  datetime.datetime.utcfromtimestamp(msg['date']).strftime('%d.%m.%Y %H:%M:%S'),
              'web': gc('webui_base'),
         }
    formatstring=('' if short else 'Reply by ')+ '@%(author)s:\n'
    if not short:
        formatstring+='>%(replytotext)s\n\n'
    formatstring+='%(text)s\n'
    if not short:
        formatstring+='\n'
    formatstring+='#%(message)s/%(id)s (%(rc)d)'
    if not short:
        formatstring+=' %(web)sp/%(message)s#%(id)s'
    return formatstring % args

def formatter_messages(request,result):
    return 'Search results:\n'+'\n\n'.join((format_message(msg,True) for msg in result['messages']))

def formatter_message_with_replies(request,result):
    return format_message(result['message']) + '\n' + \
            '\n\n'.join((format_comment(c,True) for c in result['replies']))

def formatter_subscriptions(request,result):
    return 'Your subscriptions:\n'+'\n'.join((s['type'][4:].ljust(5)+s['target'] for s in result['subscriptions']))

def formatter_message(request,result):
    return format_message(result['message'])

def formatter_recommendation(request,result):
    return 'Recommended by @%s: %s' % (result['recommender'],result['recocomment']) + \
        format_message(result['message'])

def formatter_comment(request,result):
    return format_comment(result['comment'])


