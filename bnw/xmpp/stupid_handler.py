# coding: utf-8
import traceback
from twisted.internet import defer
from twisted.internet.defer import _DefGen_Return
from twisted.words.protocols.jabber.jid import JID

import bnw.core.bnw_objects as objs
from base import CommandParserException, XmppMessage
import handlers
import iq_handlers


@defer.inlineCallbacks
def idiotic(msg):
        """Suck some cocks."""

        # return str(request.body)
        message_from = JID(msg['from'])
        message_bare_from = message_from.userhost()
        message_user = (yield objs.User.find_one({'jids': message_bare_from}))
        if not message_user:
            message_user = (yield objs.User.find_one({'jid': message_bare_from}))

        # if message.body is None:
        #    return ''

        if msg.bnw_s2s:
            bnw_s2s = msg.bnw_s2s
            print 'GOT AN s2s MESSAGE', bnw_s2s
            try:
                s2s_type = bnw_s2s['type']
            except KeyError:
                s2s_type = None
            handler = handlers.s2s_handlers.get(s2s_type)
            if not handler:
                print 'NO HANDLER FOR THIS TYPE (%s)' % (s2s_type)
            else:
                _ = yield handler(msg, bnw_s2s)
            defer.returnValue(None)
        message_body = unicode(msg.body)

        if message_body is None:
            defer.returnValue('')
        message_body = message_body.strip()
        if type(message_body) != unicode:
            message_body = unicode(message_body, 'utf-8', 'replace')
        xmsg = XmppMessage(
            message_body, JID(msg['to']), message_from, message_user)

        if message_user:
            message_user.activity()
        try:
            iparser = 'redeye'
            if message_user:
                if 'interface' in message_user:
                    iparser = message_user['interface']
            result = yield handlers.parsers[iparser].handle(xmsg)
        except CommandParserException, exc:
            result = yield exc.args[0]
        # except pymongo.errors.AutoReconnect:
        #    defer.returnValue((yield 'Sorry, our database is down.'))
        # except _DefGen_Return:
        #    raise
        except:
            # raise
            # defer.returnValue((yield "BACKEND (CATCHED) ERROR! IMMEDIATELY
            # REPORT THIS SHIT TO MY STUPID
            # AUTHOR!!!\n\n"+traceback.format_exc()))
            defer.returnValue("BACKEND (CAUGHT) ERROR! IMMEDIATELY REPORT THIS SHIT TO MY STUPID AUTHOR!!!\n\n" +
                              traceback.format_exc() + "\n" +
                              "Command which caused this exception: " + message_body)
        defer.returnValue(result)


@defer.inlineCallbacks
def failure(msg):
    _from = JID(msg['from'])
    bare_from = _from.userhost()
    user = (yield objs.User.find_one({'jid': bare_from}))  # only active jid
    if not user:
        return
    if msg.error:
        if msg.error.getAttribute('code') == '500' and msg.error.__getattr__('resource-constraint'):
            print 'User %s automatically set off because his offline storage is full.' % (user['name'],)
            objs.User.mupdate({'name': user['name']}, {'$set': {'off': True}})
            return
    print 'Unknown delivery failure'


@defer.inlineCallbacks
def iq(msg):
    """Process incoming IQ stanza."""
    try:
        iq_from = JID(msg['from'])
        iq_bare_from = iq_from.userhost()
        iq_user = (yield objs.User.find_one({'jids': iq_bare_from}))
        if not iq_user:
            iq_user = (yield objs.User.find_one({'jid': iq_bare_from}))

        for handler in iq_handlers.handlers:
            if (yield handler(msg, iq_user)):
                defer.returnValue(True)
        defer.returnValue(False)
    except Exception:
        raise
        print ("Error while processing iq:\n\n" +
               traceback.format_exc() + "\n" +
               "Command which caused this exception: " + iq)
