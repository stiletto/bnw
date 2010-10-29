# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

from base import *
import random

import pymongo

from parser_redeye import requireAuthRedeye, formatMessage, formatComment
from parser_simplified import requireAuthSimplified, formatMessageSimple, formatCommentSimple

def _(s,user):
    return s

class ShowCommand(BaseCommand):

    def handleSimplified(self,command,msg,parameters):
        _type=parameters[0]
        if _type=='last':
            messages=list(get_db().messages.find().sort('date',pymongo.DESCENDING).limit(20))
            messages.reverse()
            return 'Last 20 messages:\n%s' % ('\n'.join(formatMessageSimple(msg,short=True) for msg in messages),)
        elif _type=='tag':
            target=parameters[1][0]
            #if target[0]=='*':
            req={'tags':target.lower()}
            #elif target[1]=='!':
            #    req={'clubs':target[1:]}
            #else:
            #    return target
            messages=list(get_db().messages.find(req).sort('date',pymongo.DESCENDING).limit(20))
            messages.reverse()
            return 'Last messages with tag %s:\n%s' % ( target,
                '\n'.join(formatMessageSimple(msg,short=True) for msg in messages)
            )
        elif _type=='user':
            target=parameters[1][0]
            req={'user':target.lower()}
            messages=list(get_db().messages.find(req).sort('date',pymongo.DESCENDING).limit(20))
            messages.reverse()
            return 'Last messages from @%s:\n%s' % ( target,
                '\n'.join(formatMessageSimple(msg,short=True) for msg in messages)
            )
        elif _type=="post":
            message=get_db().messages.find_one({'id':parameters[1][0].lower()})
            if not message:
                return 'No such message.'
            if parameters[1][1]:
                reply=get_db().comments.find_one({'message':parameters[1][0].lower(),'id':parameters[1][1][1:].lower()})
                if not reply:
                    return 'No such reply.'
                return formatCommentSimple(reply,short=False)
            if not parameters[1][2]:
                return formatMessageSimple(message,short=False)
            else:
                replies=get_db().comments.find({'message':parameters[1][0].lower()}).sort('date',pymongo.ASCENDING)
                return formatMessageSimple(message,short=True)+'\n\n'+'\n\n'.join(formatCommentSimple(reply,short=True) for reply in replies)
            
    def showSearch(self,parameters,page):    
        # THIS COMMAND IS FUCKING SLOW SLOW SLOW AND WAS WRITTEN BY A BRAIN-DAMAGED IDIOT
        messages=list(get_db()['messages'].find(parameters).sort('date',pymongo.DESCENDING).limit(20).skip(page*20))
        messages.reverse()
        return ('Search results (%s):\n' % (str(parameters),)) + \
            '\n\n'.join(formatMessage(msg) for msg in messages)

    def showComments(self,msgid):
            message=get_db()['messages'].find_one({'id': msgid})
            if message is None:
                raise XmppResponse('No such message')
            return 'Full thread %s:\n%s\n\n%s' % (
                msgid, formatMessage(message),
                '\n\n'.join(formatComment(c) for c in get_db().comments.find({'message': msgid.upper()}).sort('date',pymongo.ASCENDING))
            )
        
    def handleRedeye(self,options,rest,msg):
        parameters=( ('user', options.get('user',None)),
                     ('tags', options.get('tag',None)),
                     ('clubs', options.get('club',None)),
                     ('id', options.get('message',None)) )
        parameters = dict((p[0],p[1].lower()) for p in parameters if p[1]!=None)
        if options.get('replies',False):
            if parameters.get('id',None) is None:
                raise XmppResponse('Error: -r is allowed only with -m.')
            return self.showComments(parameters['id'])
        else:
            return self.showSearch(parameters,int(options.get('page','0')))

    handleRedeye.arguments = (
        #("m", "music", , u"Post cannot be bumped to top."),
        ("m", "message", True, u"Show specified message."),
        ("u", "user", True, u"Show user's posts."),
        ("t", "tag", True, u"Show posts with tag."),
        ("c", "club", True, u"Show club posts."),
        ("p", "page", True, u"Results page (from 0)."),
        ("r", "replies", False, u"Include replies in output (only with -m)."),
        #        ("h", "human", False, u"Human-readable shits"),
        #        ("n", "number", True, u"Number of shits"),
    )

cmd = ShowCommand()
