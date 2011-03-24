# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

from base import *
import bnw_core.bnw_objects as objs

import pymongo

def _(s,user):
    return s

def findMessages(query,sort,limit):
    return objs.Message.find_sort(query,sort,limit=limit)
    
@defer.inlineCallbacks
def showSearch(parameters,page):    
    # THIS COMMAND IS FUCKING SLOW SLOW SLOW AND WAS WRITTEN BY A BRAIN-DAMAGED IDIOT
    messages=[x.filter_fields() for x in  (yield objs.Message.find_sort(
        parameters,[('date',pymongo.DESCENDING)],limit=20,skip=page*20))]
    messages.reverse()
    defer.returnValue(
        dict(ok=True,format="messages",
             messages=messages)
    )

@defer.inlineCallbacks
def showComment(commentid):
        comment=yield objs.Comment.find_one({'id': commentid})
        if comment is None:
            defer.returnValue(
                dict(ok=False,desc='No such comment')
            )
        defer.returnValue(
            dict(ok=True,format='comment',
                comment=comment.filter_fields(),
                    ))

@defer.inlineCallbacks
def showComments(msgid):
        message=yield objs.Message.find_one({'id': msgid})
        if message is None:
            defer.returnValue(
                dict(ok=False,desc='No such message')
            )
        defer.returnValue(
            dict(ok=True,format='message_with_replies',
                msgid=msgid, message=message.filter_fields(),
                replies=[comment.filter_fields() for comment in (
                    yield objs.Comment.find_sort(
                        {'message': msgid.upper()},[('date',pymongo.ASCENDING)]
                    ))
                ]
            )
        ) # suck cocks, be LISP :3

        
@check_arg(message=MESSAGE_RE+'(/'+MESSAGE_RE+')?',page='[0-9]+')
@defer.inlineCallbacks
def cmd_show(request,message="",user="",tag="",club="",page="0",replies=None):
    if '/' in message:
        defer.returnValue((yield showComment(message)))
    if replies:
        if not message:
            defer.returnValue(
                dict(ok=False,desc='Error: ''replies'' is allowed only with ''message''.')
            )
        defer.returnValue((yield showComments(message)))
    else:
        parameters=( ('user', user.lower()),
                     ('tags', tag),
                     ('clubs', club),
                     ('id', message.upper()) )
        parameters = dict((p[0],p[1]) for p in parameters if p[1])
        defer.returnValue((yield showSearch(parameters,int(page))))

@require_auth
@defer.inlineCallbacks
def cmd_feed(request):
    feed = yield objs.FeedElement.find_sort({'user':request.user['name']},
                                [('_id',pymongo.DESCENDING)],limit=20)
    messages = [x.filter_fields() for x in (yield objs.Message.find_sort({'id': { '$in': 
            [f['message'] for f in feed]
        }},[('date',pymongo.ASCENDING)]))]
    defer.returnValue(
        dict(ok=True,format="messages",
             messages=messages,
             desc='Your feed')
    )
    
