# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

from command_parsers import parsers,registerCommand
import pprint
from urllib import urlencode,quote
import time
from base import *
from uuid import uuid4
import random

from bnw.model.mongo import get_db
import pymongo

import xmlrpclib
xmlserver = xmlrpclib.Server('http://127.0.0.1:8081/RPC2')

import datetime

idchars='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'.lower()

def genid(idlen):
    return ''.join(random.choice(idchars) for i in xrange(0,idlen))

def cropstring(string,maxlen):
    return string if len(string)<=maxlen else string[:maxlen]+u'...'

def _(s,user):
    return s

#def couchdb_is_down(failure,service,msg):
#    e = failure.trap(error.ConnectError)
#    send_plain(service,msg['from'],'Error! Database is down. Request interrupted.')



registerCommand(RegisterCommand('register'))

registerCommand(SubscribeCommand('subscribe'))
registerCommand(SubscribeCommand('sub'))

registerCommand(UnSubscribeCommand('unsubscribe'))
registerCommand(UnSubscribeCommand('usub'))

registerCommand(SubscriptionsCommand('subscriptions'))
registerCommand(SubscriptionsCommand('lsub'))

registerCommand(PingCommand('ping'))
registerCommand(InterfaceCommand('interface'))

registerCommand(PostCommand('post'))
registerCommand(PostCommand('p'))

registerCommand(ShowCommand('show'))
registerCommand(ShowCommand('s'))

registerCommand(CommentCommand('comment'))
registerCommand(CommentCommand('c'))

registerCommand(HelpCommand('help',parsers['redeye']))
#commands={}
#commands['register']=RegisterCommand()
