# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

from base import *
import random

import bnw_core.bnw_objects as objs
from parser_redeye import requireAuthRedeye
from parser_simplified import requireAuthSimplified

def _(s,user):
    return s

class InterfaceCommand(BaseCommand):
    
    @requireAuthRedeye

    def handleRedeye(self,options,rest,msg): # TODO: asynchronize
        parsers=('simplified','redeye')
        if rest=='':
            defer.returnValue('Possible interfaces: '+', '.join(parsers))
        if rest in parsers:
            msg.user['interface']=rest
            _ =yield objs.User.mupdate({'name':msg.user['name']},msg.user)
            defer.returnValue('Interface changed.')
        else:
            defer.returnValue('No such interface.')
    handleRedeye.arguments= ()

    @requireAuthSimplified
    def handleSimplified(self,command,msg,parameters): # TODO: asynchronize
        defer.returnValue(self.handleRedeye({},' '.join(parameters),msg))

cmd = InterfaceCommand()
