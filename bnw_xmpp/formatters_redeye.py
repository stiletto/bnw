# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

import random
import datetime
import bnw_core.base

formatters = {
    'comment': None,
    'message': None,
    'recommendation': None,
    'message_with_replies': None,
    'messages': None,
}

def format_message(msg):
    result = '+++ [%s] %s:\n' % (
        datetime.datetime.utcfromtimestamp(msg['date']).strftime('%d.%m.%Y %H:%M:%S'),
        msg['user'],)
    if msg['tags']:
        result += 'Tags: %s\n' % (', '.join(msg['tags']),)
    if msg['clubs']:
        result += 'Clubs: %s\n' % (', '.join(msg['clubs']),)
    result += '\n%s\n' % (msg['text'],)
    result += '--- %(id)s (%(rc)d) %(base_url)sp/%(id)s' % { 
               'base_url': bnw_core.base.config.webui_base, 
               'id': msg['id'].upper(),
               'rc':    msg['replycount'],
             }
    return result
    
def format_comment(msg,short=False):
    args = { 'id':    msg['id'].split('/')[1].upper(),
             'author':msg['user'],
             'message':msg['message'].upper(),
             'replyto':None if msg['replyto'] is None else msg['replyto'].upper(),
             'replytotext': msg['replytotext'],
             'text':  msg['text'],
             'num':   msg.get('num',-1),
             'date':  datetime.datetime.utcfromtimestamp(msg['date']).strftime('%d.%m.%Y %H:%M:%S')
           }
    formatstring = '+++ [ %(date)s ] %(author)s'
    if msg['replyto']:
        formatstring += ' (in reply to %(replyto)s):\n'
    else:
        formatstring += ' (in reply to %(message)s):\n'
    if not short:
        formatstring += '>%(replytotext)s\n'
    formatstring += '\n%(text)s\n--- %(message)s/%(id)s (%(num)d) http://bnw.blasux.ru/p/%(message)s#%(id)s'
    return formatstring % args

def formatter_messages(request,result):
    return 'Search results:\n'+'\n'.join((format_message(msg) for msg in result['messages']))

def formatter_message_with_replies(request,result):
    return format_message(result['message']) + '\n' + \
            '\n'.join((format_comment(c,True) for c in result['replies']))

def formatter_subscriptions(request,result):
    return 'Your subscriptions:\n'+'\n'.join(
        (s['type'][4:].ljust(5)+s['target'].rjust(10)+' '+s.get('from','')
         for s in result['subscriptions']))

def formatter_message(request,result):
    return format_message(result['message'])

def formatter_recommendation(request,result):
    return 'Recommended by @%s: %s' % (result['recommender'],result['recocomment']) + \
        format_message(result['message'])

def formatter_comment(request,result):
    return format_comment(result['comment'])


