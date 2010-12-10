# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

from base import *
import bnw_core.bnw_objects as objs
from twisted.internet import defer


def _(s,user):
    return s

@require_auth
@defer.inlineCallbacks
def cmd_delete(request,message=None):
    if not message:
        defer.returnValue(
            dict(ok=False,desc='Usage: delete -m POST[/COMMENT]')
        )
    splitpost=message.split('/')
    message_id=splitpost[0].upper()
    comment_id=message if len(splitpost)>1 else None
    if comment_id:
        comment=yield objs.Comment.find_one({'id':comment_id,'message':message_id})
    post=yield objs.Message.find_one({'id':message_id})
    if comment_id:
        if not comment:
            defer.returnValue(
                dict(ok=False,desc='No such comment')
            )
        if comment['user']!=request.user['name'] and post['user']!=request.user['name']:
            defer.returnValue(
                dict(ok=False,desc='Not your comment and not your message.')
            )
        _ = (yield objs.Message.mupdate({'id':message_id},{'$inc': { 'replycount': -1}}))
        _ = yield objs.Comment.remove({'id':comment['id'],'message':comment['message'],'user':comment['user']})
        defer.returnValue(
            dict(ok=True,desc='Comment removed.')
        )
    else:
        if not post:
            defer.returnValue(
                dict(ok=False,desc='No such message.')
            )
        if post['user']!=request.user['name']:
            defer.returnValue(
                dict(ok=False,desc='Not your message.')
            )
        _ = yield objs.Message.remove({'id':post['id'],'user':post['user']})
        _ = yield objs.Comment.remove({'message':post['id']})
        defer.returnValue(
            dict(ok=True,desc='Message removed.')
        )
