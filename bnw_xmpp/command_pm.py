# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

from base import *
import random
from twisted.internet import defer
import bnw_core.bnw_objects as objs

from parser_redeye import requireAuthRedeye, formatMessage, formatComment
from parser_simplified import requireAuthSimplified, formatMessageSimple, formatCommentSimple
from twisted.python import log
import bnw_core.post

def _(s,user):
    return s

class PmCommand(BaseCommand):


    def usage(self):
        return 'PM @user <message>'
        
    @defer.inlineCallbacks
    def sendPM(self,user,target,text):
        if len(text)>2048:
            defer.returnValue('Too long.')
        target_user=yield objs.User.find_one({'name':target.lower()})
        if not target_user:
            defer.returnValue('No such user.')
        target_user.send_plain('PM from @%s:\n%s' % (user['name'],text))
        defer.returnValue('PM sent.')
        
    @requireAuthSimplified
    @defer.inlineCallbacks
    def handleSimplified(self,command,msg,parameters):
        if parameters[0].find(' ')==-1:
            defer.returnValue(self.usage())
        user,text=parameters[0].split(' ',1)
        if not user.startswith('@'):
            defer.returnValue(self.usage())
        else:
            user=user[1:]
        defer.returnValue((
            yield self.handleRedeye({'user':user},text,msg)
        ))
        
    @requireAuthRedeye
    @defer.inlineCallbacks
    def handleRedeye(self,options,rest,msg):
        defer.returnValue((
            yield self.sendPM(msg.user,options.get('user',''),rest)
        ))
    handleRedeye.arguments= (
            ("u", "user", True, u"Target user."),
        )

cmd = PmCommand()
