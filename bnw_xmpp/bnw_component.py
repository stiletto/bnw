import time

from zope.interface import Interface, implements
from twisted.python import log
from twisted.words.xish import domish
from twisted.words.protocols.jabber.ijabber import IService
from twisted.words.protocols.jabber import component
from twisted.web import xmlrpc

import bnw_core.bnw_objects as objs
from bnw_core.base import config
import stupid_handler

PRESENCE = '/presence'  # this is an global xpath query to use in an observer
MESSAGE = '/message'    # message xpath
IQ = '/iq'              # iq xpath


def create_reply(elem):
    """ switch the 'to' and 'from' attributes to reply to this element """
    # NOTE - see domish.Element class to view more methods
    frm = elem['from']
    elem['from'] = elem['to']
    elem['to'] = frm
    return elem


def create_presence(frm, to, childs=[], **kwargs):
    msg = domish.Element((None, "presence"))
    msg["from"] = frm
    msg["to"] = to
    for k, v in kwargs.iteritems():
        if k.startswith('_'):
            k = k[1:]
        msg[k] = v
    return msg


class LogService(component.Service):
    """
    A service to log incoming and outgoing xml to and from our XMPP component.

    """

    def transportConnected(self, xmlstream):
        xmlstream.rawDataInFn = self.rawDataIn
        xmlstream.rawDataOutFn = self.rawDataOut

    def rawDataIn(self, buf):
        log.msg("%s - RECV: %s" % (str(time.time()),
            unicode(buf, 'utf-8').encode('utf-8', 'replace')))

    def rawDataOut(self, buf):
        log.msg("%s - SEND: %s" % (str(time.time()),
            unicode(buf, 'utf-8').encode('utf-8', 'replace')))


#class MessageSender(xmlrpc.XMLRPC):
#    """An example object to be published.
#
#    Has five methods accessable by XML-RPC, 'echo', 'hello', 'defer',
#    'defer_fail' and 'fail.
#    """
#
#    def xmlrpc_send(self, jid, src, msg):
#        """Send to jid."""
#        return self.service.send_plain(jid, src, msg)


class BnwService(component.Service):
    """
    Example XMPP component service using twisted words.

    Basic Echo - We return the xml that is sent us.

    """
    implements(IService)

    def componentConnected(self, xmlstream):
        """
        This method is called when the componentConnected event gets called.
        That event gets called when we have connected and authenticated
        with the XMPP server.
        """

        self.jabberId = xmlstream.authenticator.otherHost
        self.xmlstream = xmlstream  # set the xmlstream so we can reuse it

        xmlstream.addObserver(PRESENCE, self.onPresence, 1)
        xmlstream.addObserver(IQ, self.onIq, 1)
        xmlstream.addObserver(MESSAGE, self.onMessage, 1)

    def send_plain(self, jid, src, content):
        msg = domish.Element((None, "message"))
        msg["to"] = jid
        msg["from"] = self.jabberId if (src is None) else src
        msg["type"] = 'chat'
        msg.addElement("body", content=content)
        msg.addChild(domish.Element(
            ('http://jabber.org/protocol/chatstates', 'active')))
        self.xmlstream.send(msg)

    def send_raw(self, jid, src, content):
        content["to"] = jid
        content["from"] = self.jabberId if (src is None) else src
        self.xmlstream.send(content)

    def callbackIq(self, result, original):
        if not (result or original['type'] == 'error'):
            elem = original
            frm = elem['from']
            elem['from'] = elem['to']
            elem['to'] = frm
            elem['type'] = 'error'
            elem.addElement('error')
            elem.error['type'] = 'cancel'
            elem.error.addElement('feature-not-implemented')
            self.xmlstream.send(elem)

    def onIq(self, iq):
        """Process IQ stanza."""
        gp = stupid_handler.iq(iq)
        gp.addCallback(self.callbackIq, original=iq)

    def callbackMessage(self, result, jid, stime, src, body):
        if result:
            etime = time.time() - stime
            self.send_plain(jid, src, str(result))
            t = objs.Timing({'date': stime, 'time': etime, 'command': unicode(body), 'jid': jid})
            t.save().addCallback(lambda x: None)
            log.msg("%s - PROCESSING TIME (from %s): %f" % (str(time.time()), jid, etime))
            if jid.split('/',1)[0] == config.admin_jid:
                self.send_plain(jid, src, 'I did it in %f seconds.' % (etime, ))

    def errbackMessage(self, result, jid, src):
        self.send_plain(jid, src, 'Early error: ' + str(result))

    def onMessage(self, msg):
        """
        Act on the message stanza that has just been received.

        """
        try:
            if msg['type'] != 'chat' or not msg.body:
                return
        except KeyError:  # somebody plz kick ma ass 4 dat
            return
        stime = time.time()
        if msg.request and msg.request.getAttribute("xmlns", "urn:xmpp:receipts"):
            rmsg = domish.Element((None, "message"))
            rmsg["id"] = msg["id"]
            rmsg["to"] = msg['from']
            rmsg["from"] = msg['to']
            rmsg.addChild(domish.Element((None, 'received')))
            rmsg.received['xmlns'] = 'urn:xmpp:receipts'
            self.xmlstream.send(rmsg)

        if msg.body and False:
            cmsg = domish.Element((None, "message"))
            cmsg["to"] = msg['from']
            cmsg["from"] = msg['to']
            cmsg["type"] = 'chat'
            cmsg.addChild(domish.Element(('http://jabber.org/protocol/chatstates', 'composing')))
            self.xmlstream.send(cmsg)

        gp = stupid_handler.idiotic(msg)
        #self.send_plain(msg['from'],'processing...')
        #gp=getPage('http://localhost:8080/xmpp_rpc/message', method='POST',postdata=msg.toXml().encode('utf-8','replace'),headers={'Content-Type':'application/octet-stream'})
        gp.addCallback(self.callbackMessage, jid=msg['from'], stime=stime, src=msg['to'], body=msg.body)
        gp.addErrback(self.errbackMessage, jid=msg['from'], src=msg['to'])

    def onPresence(self, prs):
        """
        Act on the presence stanza that has just been received.

        """
        prs_type = prs.getAttribute("type", "")
        send_status = False
        #print prs_type
        if prs_type == "subscribe":
            self.xmlstream.send(create_presence(prs["to"], prs["from"], _type="subscribed"))
            send_status = True
        elif prs_type == "unsubscribe":
            self.xmlstream.send(create_presence(prs["to"], prs["from"], _type="unsubscribed"))
        elif prs_type == "error":
            return
        if prs_type == "probe" or send_status:
            msg = create_presence(prs["to"], prs["from"])
            tm = time.gmtime()
            termctrl = "9600 0010 1110 0000 %02d %02d %02d" % (tm.tm_hour, tm.tm_min, tm.tm_sec)
            msg.addElement("status", content=termctrl)
            self.xmlstream.send(msg)

    def getRPC(self):
        r = xmlrpc.XMLRPC(allowNone=True)
        r.xmlrpc_send_plain = self.send_plain
        return r
