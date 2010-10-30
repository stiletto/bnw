# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

from base import *
import random
from twisted.internet import defer

from parser_redeye import requireAuthRedeye
from parser_simplified import requireAuthSimplified

def _(s,user):
    return s

class PingCommand(BaseCommand):
    redeye_name='ping'
    simplified_name='PING'
    answers = ('Pong, чо.', 
               'Pong, хуле.', 
               'Pong, блин, pong.',
               'Pong. А что я по-твоему должен был ответить?',
               'Pong です！',
               'Pong. А ты с какова раёна будешь?',
               'Pong. А ты знаешь об опции -s / --safe?')
    
    def usageHelp(self):
        return 'Usage: %s [-s|--safe]' % (self.redeye_name,)

    @requireAuthSimplified
    @defer.inlineCallbacks
    def handleSimplified(self,command,msg,parameters):
        defer.returnValue(random.choice(self.answers))
        
    @requireAuthRedeye
    @defer.inlineCallbacks
    def handleRedeye(self,options,rest,msg):
        defer.returnValue('Pong.' if options.get('safe',False) else random.choice(self.answers))
    handleRedeye.arguments= (
            ("s", "safe", False, u"Do not vyebyvatsya."),
        )

cmd = PingCommand()
