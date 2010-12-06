# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

from base import *
import random
from twisted.internet import defer

def _(s,user):
    return s

class ExceptCommand(BaseCommand):
    redeye_name='except'
    
    def handleRedeye(self,options,rest,msg):
        raise Exception('Хуйпизда!')
    handleRedeye.arguments= (
        )

cmd = ExceptCommand()
