# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

from base import *
import random
import bnw_core.bnw_objects as objs

from parser_redeye import requireAuthRedeye, formatMessage, formatComment
from parser_simplified import requireAuthSimplified, formatMessageSimple, formatCommentSimple
from twisted.python import log
import bnw_core.post

def _(s,user):
    return s

def throttle_check(user):
    post_throttle=get_db()['post_throttle'].find_one({'user':user})
    if post_throttle and post_throttle['time']>=(time.time()-5):
        raise XmppResponse('You are sending messages too fast!')
    return post_throttle
    
def throttle_update(user,post_throttle):
        db=yield get_db()
        throttledoc={'user':user,'time':time.time()}
        if post_throttle:
            yield db['post_throttle'].update({'user':user},throttledoc)
        else:
            yield db['post_throttle'].insert(throttledoc)
        defer.returnValue(None)

class PostCommand(BaseCommand):
    redeye_name='post'

    @requireAuthSimplified
    @defer.inlineCallbacks
    def handleSimplified(self,command,msg,parameters):
        groups=parameters[0]
        tags=[a[1:] for a in filter(None,groups[0:4])]
        text=groups[5]
        defer.returnValue((yield self.postMessage(msg,tags,[],text)))

    @defer.inlineCallbacks
    def postMessage(self,msg,tags,clubs,text,anon=False,anoncom=False):
        post_throttle=yield throttle_check(msg.user['name'])
        rest = yield bnw_core.post.postMessage(msg.user,tags,clubs,text,anon,anoncom)
        if type(rest)==tuple:
            qn,recepients = rest
        else:
            defer.returnValue(rest)
        _ = yield throttle_update(msg.user['name'],post_throttle)
        defer.returnValue('Posted with id %s. Delivered to %d users. Total cost: $%d' % (message['id'].upper(),recepients,qn))

    @requireAuthRedeye
    @defer.inlineCallbacks
    def handleRedeye(self,options,rest,msg):
        tags=options['tags'].split(',')[:5] if 'tags' in options else []
        clubs=options['clubs'].split(',')[:5] if 'clubs' in options else []
        tags=map(lambda x: x.replace('\n',' '),map(unicode.lower,tags))
        clubs=map(lambda x: x.replace('\n',' '),map(unicode.lower,clubs))
        defer.returnValue((yield self.postMessage(msg,tags,clubs,rest,options.get('anonymous',False),options.get('anonymous-comments',False))))
    handleRedeye.arguments = (
        ("s", "notop", False, u"Post cannot be bumped to top."), # no-op
        ("t", "tags", True, u"Mark post with this tag(s) (comma-separated)."),
        ("c", "clubs", True, u"Post to this club(s) (comma-separated)."),
        ("a", "anonymous", False, u"Anonymous post."),
        ("q", "anonymous-comments", False, u"Make all comments to this post anonymous (doesn''t work at all yet)."),
    )

class CommentCommand(BaseCommand):
    redeye_name='post'

    @defer.inlineCallbacks
    def postComment(self,message_id,comment_id,rest,msg,anon=False):
        post_throttle=yield throttle_check(msg.user['name'])
        rest = yield bnw_core.post.postComment(message_id,comment_id,rest,msg.user,anon)
        if type(rest)==tuple:
            qn,recepients = rest
        else:
            defer.returnValue(rest)
        _ = yield throttle_update(msg.user['name'],post_throttle)
        #log.debug
        defer.returnValue('Posted with id %s. Delivered to %d users. Total cost: $%d' % (message['id'].upper(),recepients,qn))

    @requireAuthSimplified
    @defer.inlineCallbacks
    def handleSimplified(self,command,msg,parameters):
        message_id=parameters[0][0].upper()
        if parameters[0][1]:
            #raise Exception(parameters[0][1])
            comment_id=parameters[0][1][1:].upper()
        else:
            comment_id=None
        defer.returnValue((yield self.postComment(message_id,comment_id,parameters[0][2],msg)))

    @requireAuthRedeye
    @defer.inlineCallbacks
    def handleRedeye(self,options,rest,msg):
        qn=0
        message_id=options.get('message',None)
        if message_id==None:
            raise XmppResponse('You must specify a message to comment.')
        msplit=message_id.upper().split('/',1)
        message_id=msplit[0]
        if len(msplit)>1:
            comment_id=msplit[1]
        else:
            comment_id=None
            
        defer.returnValue((yield self.postComment(message_id,comment_id,rest,msg,options.get('anonymous',False))))
    handleRedeye.arguments = (
        ("m", "message", True, u"Message to comment."),
        ("a", "anonymous", False, u"Anonymous comment."),
    )

postcmd = PostCommand()
commentcmd = CommentCommand()
