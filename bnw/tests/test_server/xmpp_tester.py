from twisted.python import log
from twisted.internet import defer
from twisted.words.protocols.jabber import error, ijabber, jstrports, xmlstream
from twisted.words.protocols.jabber import component

class XmppTestServerFactory(xmlstream.XmlStreamServerFactory):
    def __init__(self, starter):
        def authenticatorFactory():
            return component.ListenComponentAuthenticator('test')

        xmlstream.XmlStreamServerFactory.__init__(self, authenticatorFactory)
        self.addBootstrap(xmlstream.STREAM_CONNECTED_EVENT,
                          self.onConnectionMade)
        self.addBootstrap(xmlstream.STREAM_AUTHD_EVENT,
                          self.onAuthenticated)

        self.cstate = 0
        self.component = None
        self.listeners = []
        self.queue = []
        self.starter = starter


    def onConnectionMade(self, xs):
        log.msg("New connection: %r" % (xs,))
        assert self.cstate == 0
        self.cstate = 1

        def logDataIn(buf):
            log.msg("RECV (tf): %r" % (buf,))

        def logDataOut(buf):
            log.msg("SEND (tf): %r" % (buf,))

        xs.rawDataInFn = logDataIn
        xs.rawDataOutFn = logDataOut

        xs.addObserver(xmlstream.STREAM_ERROR_EVENT, self.onError)


    def onAuthenticated(self, xs):
        assert self.cstate == 1
        self.cstate = 2
        destination = xs.thisEntity.host

        self.component = xs
        xs.addObserver(xmlstream.STREAM_END_EVENT, self.onConnectionLost, 0,
                                                   destination, xs)
        xs.addObserver('/*', self.onStanza)
        self.starter(self)


    def onError(self, reason):
        log.err(reason, "Stream Error")


    def onConnectionLost(self, destination, xs, reason):
        assert self.cstate > 0
        xs.removeObserver('/*', self.onStanza)
        self.component = None
        self.cstate = 0

    def onStanza(self, stanza):
        while self.listeners and self.queue:
            listener = self.listeners.pop(0)
            queued_stanza = self.queue.pop(0)
            listener.callback(queued_stanza)
        if self.listeners:
            listener = self.listeners.pop(0)
            listener.callback(stanza)
        else:
            self.queue.append(stanza)

    def stanzaReset(self):
        self.listeners = []
        self.queue = []

    def stanzaRecv(self):
        d = defer.Deferred()
        if self.queue:
            d.callback(self.queue.pop(0))
        else:
            self.listeners.append(d)
        return d

    def stanzaSend(self, stanza):
        self.component.send(stanza)

