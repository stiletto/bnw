# coding: utf-8
import bnw_xmpp
from bnw_xmpp.base import CommandParserException, XmppMessage, get_db
import bnw_core.bnw_objects as objs
import pymongo
import traceback
import bnw_xmpp.handlers
from twisted.internet import defer
from twisted.internet.defer import _DefGen_Return

@defer.inlineCallbacks
def idiotic(msg):
        """Suck some cocks."""
                                                                                                    
        #return str(request.body)
        message_from=msg['from']
        message_bare_from=message_from.split('/',1)[0]
        message_user=(yield objs.User.find_one({'jid':message_bare_from.lower()}))
        #if message.body is None:
        #    return ''

        message_body=unicode(msg.body)

        if message_body is None:
            defer.returnValue('')
        message_body=message_body.strip()
        if type(message_body)!=unicode:
            message_body=unicode(message_body,'utf-8','replace')
        xmsg=XmppMessage(message_body,message_from,message_bare_from,message_user)

        try:
            iparser='redeye'
            if message_user:
                if 'interface' in message_user:
                    iparser=message_user['interface']
            defer.returnValue((yield bnw_xmpp.handlers.parsers[iparser].handleCommand(xmsg)))
        except CommandParserException, exc:
            defer.returnValue((yield exc.args[0]))
        #except pymongo.errors.AutoReconnect:
        #    defer.returnValue((yield 'Sorry, our database is down.'))
        except _DefGen_Return:
            raise
        except:
            #raise
            #defer.returnValue((yield "BACKEND (CATCHED) ERROR! IMMEDIATELY REPORT THIS SHIT TO MY STUPID AUTHOR!!!\n\n"+traceback.format_exc()))
            defer.returnValue("BACKEND (CATCHED) ERROR! IMMEDIATELY REPORT THIS SHIT TO MY STUPID AUTHOR!!!\n\n"+\
                traceback.format_exc()+"\n"+\
                "Command which caused this exception: "+message_body)

