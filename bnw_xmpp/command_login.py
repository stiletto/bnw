# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

from base import *
import bnw_core.base
import random
from twisted.internet import defer

from parser_redeye import requireAuthRedeye
from parser_simplified import requireAuthSimplified

def _(s,user):
    return s

class LoginCommand(BaseCommand):

    @requireAuthSimplified
    @defer.inlineCallbacks
    def handleSimplified(self,command,msg,parameters):
        defer.returnValue(bnw_core.base.config.webui_base+'login?key='+msg.user.get('login_key',''))
        
    @requireAuthRedeye
    @defer.inlineCallbacks
    def handleRedeye(self,options,rest,msg):
        defer.returnValue((yield self.handleSimplified(None,msg,None)))
    handleRedeye.arguments= (
        )

cmd = LoginCommand()
