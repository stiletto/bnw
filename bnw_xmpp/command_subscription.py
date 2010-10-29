# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

from base import *
import random


from parser_redeye import requireAuthRedeye
from parser_simplified import requireAuthSimplified

def _(s,user):
    return s

class SubscribeCommand(BaseCommand):
    redeye_name='subscribe'
    
    def usageHelp(self):
        return 'Usage: %s <-u username|-t tag|-c club|-m message>' % (self.redeye_name,)

    def parseSubscription(self,options,msg):
        for stype in ['message','user','club','tag']:
            if options.get(stype)!=None:
                return { 'user': msg.user['name'], 'target': options[stype].lower(), 'type': 'sub_'+stype }
        raise XmppResponse(self.usageHelp())
    
    stypes={ '*': 'tag', '!': 'club', '@': 'user', '#': 'message' }
    srtypes = dict((d[1],d[0]) for d in stypes.items())
    def parseSimplifiedSub(self,sub,msg):
        if not sub[0] in self.stypes:
            raise XmppResponse('Unknown subscription type')
        return { 'user': msg.user['name'], 'target': sub[1:], 'type': 'sub_'+self.stypes[sub[0]] }
        
    @requireAuthSimplified
    def handleSimplified(self,command,msg,parameters):
        if len(parameters)==0: # show subscriptions
            return 'Your subscriptions:\n'+\
                '\n'.join((self.srtypes[x['type'][4:]]+x['target']) for x in get_db().subscriptions.find({'user':msg.user['name']}))
        else:
            sub_rec=self.parseSimplifiedSub(parameters[0],msg)
            if get_db()['subscriptions'].find_one(sub_rec) is None: 
                get_db()['subscriptions'].insert(sub_rec)
                return 'Subscribed.'
            else:
                return 'Already subscribed.'
    
    @requireAuthRedeye
    def handleRedeye(self,options,rest,msg):
        sub_rec=self.parseSubscription(options,msg)
        if get_db()['subscriptions'].find_one(sub_rec) is None: 
            # actually it's not fatal if duplicate subscription records appear,
            # so we won't seriously care about it
            get_db()['subscriptions'].insert(sub_rec)
            return 'Subscribed.'
        else:
            return 'Already subscribed.'
    handleRedeye.arguments = (
        ("m", "message", True, u"Subscribe to message."),
        ("u", "user", True, u"Subscribe to user."),
        ("t", "tag", True, u"Subscribe to tag."),
        ("c", "club", True, u"Subscribe to club."),
    )

class UnSubscribeCommand(SubscribeCommand): # unsubscription is a special case of subscription, lol
    redeye_name='unsubscribe'

    @requireAuthRedeye
    def handleRedeye(self,options,rest,msg):
        sub_rec=self.parseSubscription(options,msg)
        get_db()['subscriptions'].remove(sub_rec) # even if there was no such subscription, we don't care
        return 'Unsubscribed.' 
    handleRedeye.arguments=SubscribeCommand.handleRedeye.arguments
    
    @requireAuthSimplified
    def handleSimplified(self,command,msg,parameters):
        sub_rec=self.parseSimplifiedSub(parameters[0],msg)
        get_db()['subscriptions'].remove(sub_rec) # even if there was no such subscription, it won't hurt
        return 'Unsubscribed.' 


class SubscriptionsCommand(BaseCommand):
    redeye_name='subscriptions'
    
    subchars = {
        "sub_message": "message ",
        "sub_user": "user ",
        "sub_tag":  "tag  ",
        "sub_club": "club ",
    }
    
    
    @requireAuthRedeye
    def handleRedeye(self,options,rest,msg):
        incmsg=options.get('messages',False)
        return 'You subscriptions:\n' + \
            '\n'.join(
                self.subchars[sub['type']]+sub['target'] for sub in
                    get_db()['subscriptions'].find({ 'user': msg.user['name']}).sort('type',pymongo.ASCENDING) if incmsg or sub['type']!='sub_message'
            )
    handleRedeye.arguments=(
        ('m','messages',False,'Include messages'),
    )


sub = SubscribeCommand()
usub = UnSubscribeCommand()
lsub = SubscriptionsCommand()

