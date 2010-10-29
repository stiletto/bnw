# -*- coding: utf8 -*-
"""
 Example component service.
 
"""
import time
from twisted.words.protocols.jabber import jid, xmlstream
from twisted.application import internet, service
from twisted.internet import interfaces, defer, reactor
from twisted.python import log
from twisted.words.xish import domish


from twisted.words.protocols.jabber.ijabber import IService
from twisted.words.protocols.jabber import component

from zope.interface import Interface, implements

PRESENCE = '/presence' # this is an global xpath query to use in an observer
MESSAGE  = '/message'  # message xpath 
IQ       = '/iq'       # iq xpath

def create_reply(elem):
    """ switch the 'to' and 'from' attributes to reply to this element """
    # NOTE - see domish.Element class to view more methods 
    frm = elem['from']
    elem['from'] = elem['to']
    elem['to']   = frm

    return elem

class LogService(component.Service):
    """
    A service to log incoming and outgoing xml to and from our XMPP component.

    """
    
    def transportConnected(self, xmlstream):
        xmlstream.rawDataInFn = self.rawDataIn
        xmlstream.rawDataOutFn = self.rawDataOut

    def rawDataIn(self, buf):
        log.msg("%s - RECV: %s" % (str(time.time()), unicode(buf, 'utf-8').encode('ascii', 'replace')))

    def rawDataOut(self, buf):
        log.msg("%s - SEND: %s" % (str(time.time()), unicode(buf, 'utf-8').encode('ascii', 'replace')))


class ExampleService(component.Service):
    """
    Example XMPP component service using twisted words.

    Basic Echo - We return the xml that is sent us.
    
    """
    implements(IService)

        
    def componentConnected(self, xmlstream):
        """
        This method is called when the componentConnected event gets called.
        That event gets called when we have connected and authenticated with the XMPP server.
        """
        
        self.jabberId = xmlstream.authenticator.otherHost
        self.xmlstream = xmlstream # set the xmlstream so we can reuse it
        
        xmlstream.addObserver(PRESENCE, self.onPresence, 1)
        xmlstream.addObserver(IQ, self.onIq, 1)
        xmlstream.addObserver(MESSAGE, self.onMessage, 1)

    def onMessage(self, msg):
        """
        Act on the message stanza that has just been received.

        """
    
        # return to sender

        msg = create_reply(msg)

        self.xmlstream.send(msg) # send the modified domish.Element 
        
        
    def onIq(self, iq):
        """
        Act on the iq stanza that has just been received.

        """

        #iq = create_reply(iq)
        #self.xmlstream.send(iq)
        pass
            
    def onPresence(self, prs):
        """
        Act on the presence stanza that has just been received.

        """
        prs = create_reply(prs)
        self.xmlstream.send(prs)
