#!/bin/echo tac is a python source file, but should be started via twistd

import sys
try:
    sys.setappdefaultencoding('utf-8')
except:
    sys = reload(sys)
    sys.setdefaultencoding('utf-8')

import tornado.platform.twisted
tornado.platform.twisted.install()

from twisted.application import service, internet
from twisted.words.protocols.jabber import component
from twisted.web import server
from twisted.manhole.telnet import ShellFactory
from time import time
import traceback
import config
import bnw.core.base
import bnw.core.ensure_indexes
import bnw.xmpp.base
from bnw.core.bnw_mongo import open_db
from bnw.xmpp import bnw_component, xmpp_notifier
from bnw.handlers import throttle, mapreduce

bnw.core.base.config.register(config)
application = service.Application("BnW")

open_db()

from twisted.internet import reactor
reactor.callWhenRunning(bnw.core.ensure_indexes.index)

# Set up XMPP component.
sm = component.buildServiceManager(
    config.srvc_name, config.srvc_pwd,
    ('tcp:'+config.xmpp_server))

# Turn on verbose mode.
bnw_component.LogService().setServiceParent(sm)

# Set up our service.
s = bnw_component.BnwService()
s.setServiceParent(sm)

bnw.xmpp.base.service.register(s)
bnw.core.base.notifiers.add(xmpp_notifier.XmppNotifier())

serviceCollection = service.IServiceCollection(application)
sm.setServiceParent(serviceCollection)

def parse_port(port):
    if isinstance(port, str) and ':' in port:
        host, port = port.rsplit(":", 1)
        return host, int(port)
    return "127.0.0.1", int(port)

if config.trace_shutdown:
    def beforeandaftershutdown(when):
        import inspect
        print '%s shutdown:' % (when,)
        evt=reactor._eventTriggers.get('shutdown')
        print 'Before:',evt.before
        print 'During:',evt.during
        print 'After:',evt.after
        for k,v in sys._current_frames().iteritems():
            print '%s: %s:%s' % (k,inspect.getfile(v),v.f_lineno)
            traceback.print_stack(v)
    reactor.addSystemEventTrigger('before', 'shutdown', beforeandaftershutdown, 'Before')
    reactor.addSystemEventTrigger('during', 'shutdown', beforeandaftershutdown, 'During')
    reactor.addSystemEventTrigger('after', 'shutdown', beforeandaftershutdown, 'After')

if config.rpc_enabled:
    rpc_host, rpc_port = parse_port(config.rpc_port)
    internet.TCPServer(
        rpc_port, server.Site(s.getRPC()),
        interface=rpc_host).setServiceParent(serviceCollection)

if config.statsd:
    from bnw.core import statsd
    statsd.setup(*parse_port(config.statsd))

if config.manhole:
    shell_factory = ShellFactory()
    shell_factory.password = config.manhole
    shell_tcp_server = internet.TCPServer(4040, shell_factory, interface="127.0.0.1")
    shell_tcp_server.setServiceParent(serviceCollection)

if config.webui_enabled:
    import bnw.web.site
    http_server = bnw.web.site.get_site()
    webui_host, webui_port = parse_port(config.webui_port)
    http_server.listen(webui_port, webui_host)

bnw.core.base.timertime = 0
def checkload(lasttime):
    currenttime = time()
    if lasttime is not None:
        bnw.core.base.timertime = currenttime - lasttime
    reactor.callLater(1, checkload, currenttime)
checkload(None)

throttle.setup_throttle()
mapreduce.setup_mapreduce()

def runintwistd():
    sys.argv.insert(1,__file__)
    sys.argv.insert(1,'-y')
    from twisted.scripts.twistd import run
