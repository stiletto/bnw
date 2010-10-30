# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

from base import *
import bnw_core.bnw_objects as objs
import random

import pymongo

from parser_redeye import requireAuthRedeye, formatMessage, formatComment
from parser_simplified import requireAuthSimplified, formatMessageSimple, formatCommentSimple

def _(s,user):
    return s

class ShowCommand(BaseCommand):

    def findMessages(self,query,sort,limit):
        return objs.Message.find_sort(query,sort,limit=limit)
    
    @defer.inlineCallbacks
    def handleSimplified(self,command,msg,parameters):
        _type=parameters[0]
        if _type=='last':
            messages=list((yield self.findMessages({},[('date',pymongo.DESCENDING)],20)))
            messages.reverse()
            defer.returnValue('Last 20 messages:\n%s' % (
                '\n'.join(formatMessageSimple(msg,short=True) for msg in messages),)
            )
        elif _type=='tag':
            target=parameters[1][0]
            req={'tags':target.lower()}
            messages=list((yield self.findMessages(req,[('date',pymongo.DESCENDING)],20)))
            messages.reverse()
            defer.returnValue('Last messages with tag %s:\n%s' % ( target,
                '\n'.join(formatMessageSimple(msg,short=True) for msg in messages)
            ))
        elif _type=='user':
            target=parameters[1][0]
            req={'user':target.lower()}
            messages=list((yield self.findMessages(req,[('date',pymongo.DESCENDING)],20)))
            messages.reverse()
            defer.returnValue('Last messages from @%s:\n%s' % ( target,
                '\n'.join(formatMessageSimple(msg,short=True) for msg in messages)
            ))
        elif _type=="post":
            msg_id=parameters[1][0].upper()
            message=yield objs.Message.find_one({'id':msg_id})
            if not message:
                defer.returnValue('No such message.')
            if parameters[1][1]:
                comment_id=parameters[1][1][1:].upper()
                reply=FUCK.comments.find_one({'message':msg_id,'id':comment_id})
                if not reply:
                    defer.returnValue('No such reply.')
                defer.returnValue(formatCommentSimple(reply,short=False))
            if not parameters[1][2]:
                defer.returnValue(formatMessageSimple(message,short=False))
            else:
                replies=yield objs.Comment.find_sort(
                    {'message':msg_id},
                    [('date',pymongo.ASCENDING)]
                )
                defer.returnValue(
                    formatMessageSimple(message,short=True)+'\n\n'+ \
                    '\n\n'.join(formatCommentSimple(reply,short=True) for reply in replies))

    @defer.inlineCallbacks
    def showSearch(self,parameters,page):    
        # THIS COMMAND IS FUCKING SLOW SLOW SLOW AND WAS WRITTEN BY A BRAIN-DAMAGED IDIOT
        messages=list((yield objs.Message.find_sort(
            parameters,[('date',pymongo.DESCENDING)],limit=20,skip=page*20)))
        messages.reverse()
        defer.returnValue(('Search results (%s):\n' % (str(parameters),)) + \
            '\n\n'.join(formatMessage(msg) for msg in messages))

    @defer.inlineCallbacks
    def showComments(self,msgid):
            message=yield objs.Message.find_one({'id': msgid})
            if message is None:
                raise XmppResponse('No such message')
            defer.returnValue('Full thread %s:\n%s\n\n%s' % (
                msgid, formatMessage(message),
                '\n\n'.join(formatComment(c) for c in
                    (yield objs.Comment.find_sort({'message': msgid.upper()},[('date',pymongo.ASCENDING)]))
            )))
        
    @defer.inlineCallbacks
    def handleRedeye(self,options,rest,msg):
        parameters=( ('user', options.get('user',None)),
                     ('tags', options.get('tag',None)),
                     ('clubs', options.get('club',None)),
                     ('id', options.get('message',None)) )
        parameters = dict((p[0],p[1].lower()) for p in parameters if p[1]!=None)
        if 'id' in parameters: # down and up, bitch
            parameters['id']=parameters['id'].upper()
        if options.get('replies',False):
            if parameters.get('id',None) is None:
                raise XmppResponse('Error: -r is allowed only with -m.')
            defer.returnValue((yield self.showComments(parameters['id']) ))
        else:
            defer.returnValue((yield self.showSearch(parameters,int(options.get('page','0')))))

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
