# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

from base import *
import bnw_core.bnw_objects as objs
from twisted.internet import defer
import random


from parser_redeye import requireAuthRedeye
from parser_simplified import requireAuthSimplified

def _(s,user):
    return s

class DeleteCommand(BaseCommand):
    @requireAuthRedeye
    @defer.inlineCallbacks
    def handleRedeye(self,options,rest,msg): # TODO: asynchronize
        if not 'message' in options:
            defer.returnValue('Usage: delete -m POST[/COMMENT]')
        splitpost=options['message'].split('/')
        message_id=splitpost[0].upper()
        comment_id=splitpost[1].upper() if len(splitpost)>1 else None
        if comment_id:
            comment=yield objs.Comment.find_one({'id':comment_id,'message':message_id})
        message=yield objs.Message.find_one({'id':message_id})
        if comment_id:
            if comment['user']!=msg.user['name'] and message['user']!=msg.user['name']:
                defer.returnValue('Not your comment and not your message.')
            _ = yield objs.Comment.remove({'id':comment['id'],'message':comment['message'],'user':comment['user']})
            defer.returnValue('Comment removed.')
        else:
            if message['user']!=msg.user['name']:
                defer.returnValue('Not your message.')
            _ = yield objs.Message.remove({'id':message['id'],'user':message['user']})
            _ = yield objs.Comment.remove({'message':message['id']})
            defer.returnValue('Message removed.')
    handleRedeye.arguments= (
        ('m',   'message',True,'Message or comment to delete.'),
    )
            

    @requireAuthSimplified
    @defer.inlineCallbacks
    def handleSimplified(self,command,msg,parameters):
        postid=parameters[0]
        if not postid.startswith('#'):
            defer.returnValue('Usage: D #POST[/COMMENT]')
        defer.returnValue((yield self.handleRedeye({'message':postid[1:]},'',msg)))

    
cmd = DeleteCommand()
