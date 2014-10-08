from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

COUNTER = 'c'
TIMING = 'ms'
GAUGE = 'g'
SET = 's'

class StatsD(DatagramProtocol):
    def __init__(self, host=None, port=None):
        self.host = host
        self.port = port
        self.usable = False

    def startProtocol(self):
        self.usable = True
        self.transport.connect(self.host, self.port)

    def stopProtocol(self):
        self.usable = False

    def datagramReceived(self, data, (host, port)):
        pass

    def connectionRefused(self):
        pass

    def sendMetric(self, metric, value, _type, at=None):
        if self.usable:
            packet = "%s:%d|%s" % (metric, value, _type)
            if at:
                packet += "|@%s" % (at, )
            self.transport.write(packet)


client = StatsD(None, None)
send = client.sendMetric

def setup(host, port):
    client.host = host
    client.port = port
    reactor.listenUDP(0, client, interface=host if host=='127.0.0.1' else '')
