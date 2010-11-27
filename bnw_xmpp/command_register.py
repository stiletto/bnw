# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

from base import *
import random


from parser_redeye import requireAuthRedeye
from parser_simplified import requireAuthSimplified

def _(s,user):
    return s
from uuid import uuid4
import re

NAME_RE=re.compile('^[0-9A-Za-z_-]+$')
class RegisterCommand(BaseCommand):
    redeye_name='register'

    def usageHelp(self):
        return 'Usage %s <nickname>\n\tNickname must be alphanumeric' % (self.redeye_name,)

    @defer.inlineCallbacks
    def handleRedeye(self,options,rest,msg):
        if msg.user:
            raise XmppResponse(_(u'You are already registered as %s',msg.user) % (msg.user['name'],))
        else:
            if not (NAME_RE.match(rest)):
                raise XmppResponse(self.usageHelp())

            rest=rest.lower()
            if rest=='anonymous':
                raise XmppResponse(u'You aren''t anonymous.')
                
            user={ 'id': uuid4().hex,
                   'name': rest,
                   'login_key': uuid4().hex,
                   'regdate': int(time.time()),
                   'jid': msg.bare_jid,
                 }
            if not (yield (yield get_db())['users'].find_one({'name':rest})):
                (yield get_db())['users'].insert(user)
                defer.returnValue('We registered you as %s.' % (rest,))
            else:
                defer.returnValue('This username is already taken')
    handleRedeye.arguments= ()

cmd = RegisterCommand()
