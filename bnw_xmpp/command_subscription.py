# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

from base import *
import random


from parser_redeye import requireAuthRedeye
from parser_simplified import requireAuthSimplified

import bnw_core.bnw_objects as objs
import bnw_core.post
import pymongo

def _(s,user):
    return s

class SubscribeCommand(BaseCommand):
    redeye_name='subscribe'
    
    def usageHelp(self):
        return 'Usage: %s <-u username|-t tag|-c club|-m message>' % (self.redeye_name,)

    def parseSubscription(self,options,msg):
        for stype in ['message','user','club','tag']:
            if options.get(stype)!=None:
                return options[stype].lower(), 'sub_'+stype
        raise XmppResponse(self.usageHelp())
    
    stypes={ '*': 'tag', '!': 'club', '@': 'user', '#': 'message' }
    srtypes = dict((d[1],d[0]) for d in stypes.items())
    def parseSimplifiedSub(self,sub,msg):
        if not sub[0] in self.stypes:
            raise XmppResponse('Unknown subscription type')
        return sub[1:], 'sub_'+self.stypes[sub[0]]
        
    @requireAuthSimplified
    @defer.inlineCallbacks
    def handleSimplified(self,command,msg,parameters):
        if len(parameters)==0: # show subscriptions
            defer.returnValue('Your subscriptions:\n'+\
                '\n'.join((
                self.srtypes[x['type'][4:]]+x['target']) for x in
                (yield objs.Subscription.find({'user':msg.user['name'],
                    'type':{'$ne':'sub_message'}}))
                ))
        else:
            starget,stype=self.parseSimplifiedSub(parameters[0],msg)
            defer.returnValue((yield bnw_core.post.subscribe(msg.user, stype, starget)))
    
    @requireAuthRedeye
    @defer.inlineCallbacks
    def handleRedeye(self,options,rest,msg):
        starget,stype=self.parseSubscription(options,msg)
        if options.get('newtab',False):
            subc=''.join(c for c in starget[:10] if (c>='a' and c<='z'))
            sfrom=stype[4]+'-'+subc
        else:
            sfrom=msg.to
        defer.returnValue((yield bnw_core.post.subscribe(msg.user, stype, starget,sfrom=sfrom)))
    handleRedeye.arguments = (
        ("m", "message", True, u"Subscribe to message."),
        ("u", "user", True, u"Subscribe to user."),
        ("t", "tag", True, u"Subscribe to tag."),
        ("c", "club", True, u"Subscribe to club."),
        ("n", "newtab", False, u"Receive messages for this subscription from into tab"),
    )

class UnSubscribeCommand(SubscribeCommand): # unsubscription is a special case of subscription, lol
    redeye_name='unsubscribe'

    @requireAuthRedeye
    @defer.inlineCallbacks
    def handleRedeye(self,options,rest,msg):
        starget,stype=self.parseSubscription(options,msg)
        rest=yield bnw_core.post.unsubscribe(msg.user, stype, starget)
        defer.returnValue('Unsubscribed.')
    handleRedeye.arguments=SubscribeCommand.handleRedeye.arguments
    
    @requireAuthSimplified
    @defer.inlineCallbacks
    def handleSimplified(self,command,msg,parameters):
        starget,stype=self.parseSimplifiedSub(parameters[0],msg)
        rest=yield bnw_core.post.unsubscribe(msg.user, stype, starget)
        defer.returnValue('Unsubscribed.')

class SubscriptionsCommand(BaseCommand):
    redeye_name='subscriptions'
    
    subchars = {
        "sub_message": "message ",
        "sub_user": "user ",
        "sub_tag":  "tag  ",
        "sub_club": "club ",
    }
    
    
    @requireAuthRedeye
    @defer.inlineCallbacks
    def handleRedeye(self,options,rest,msg):
        incmsg=options.get('messages',False)
        defer.returnValue('You subscriptions:\n' + \
            '\n'.join(
                self.subchars[sub['type']]+sub['target'] for sub in
                (yield objs.Subscription.find_sort({ 'user': msg.user['name'],
                    'type':{'$ne':'sub_message'}},
                    [('type',pymongo.ASCENDING)]))
                if incmsg or sub['type']!='sub_message'
            )
        )
    handleRedeye.arguments=(
        ('m','messages',False,'Include messages'),
    )


sub = SubscribeCommand()
usub = UnSubscribeCommand()
lsub = SubscriptionsCommand()

