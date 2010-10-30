# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

from base import *
import random

import bnw_base.bnw_objects as objs
from parser_redeye import requireAuthRedeye
from parser_simplified import requireAuthSimplified

def _(s,user):
    return s

class OnCommand(BaseCommand):
    @requireAuthRedeye
    @defer.inlineCallbacks
    def handleRedeye(self,options,rest,msg):
        msg.user['off']=False
        _ = yield objs.User.update({'name':msg.user['name']},msg.user)
        defer.returnValue('Welcome back!')
    handleRedeye.arguments= ()

    @requireAuthSimplified
    @defer.inlineCallbacks
    def handleSimplified(self,command,msg,parameters):
        defer.returnValue(self.handleRedeye({},' '.join(parameters),msg))


class OffCommand(OnCommand):
    @requireAuthRedeye
    @defer.inlineCallbacks
    def handleRedeye(self,options,rest,msg):
        msg.user['off']=True
        _ = yield objs.User.update({'name':msg.user['name']},msg.user)
        defer.returnValue('C u l8r!')
    handleRedeye.arguments= ()

oncmd = OnCommand()
offcmd = OffCommand()
