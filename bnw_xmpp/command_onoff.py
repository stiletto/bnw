# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

from base import *
import random


from parser_redeye import requireAuthRedeye
from parser_simplified import requireAuthSimplified

def _(s,user):
    return s

class OnCommand(BaseCommand):
    @requireAuthRedeye
    def handleRedeye(self,options,rest,msg):
        msg.user['off']=False
        get_db().users.update({'name':msg.user['name']},msg.user)
        defer.returnValue('Welcome back!')
    handleRedeye.arguments= ()

    @requireAuthSimplified
    def handleSimplified(self,command,msg,parameters):
        defer.returnValue(self.handleRedeye({},' '.join(parameters),msg))


class OffCommand(OnCommand):
    @requireAuthRedeye
    def handleRedeye(self,options,rest,msg):
        msg.user['off']=True
        get_db().users.update({'name':msg.user['name']},msg.user)
        defer.returnValue('C u l8r!')
    handleRedeye.arguments= ()

oncmd = OnCommand()
offcmd = OffCommand()
