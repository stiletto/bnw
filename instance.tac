#!/bin/echo tac is a python source file, but should be started via twistd

import sys
try:
    sys.setappdefaultencoding('utf-8')
except:
    sys = reload(sys)
    sys.setdefaultencoding('utf-8')
import os.path
root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, root)

import tornado.platform.twisted
tornado.platform.twisted.install()

from twisted.application import service, internet
from twisted.words.protocols.jabber import component
from twisted.web import server
from twisted.manhole.telnet import ShellFactory
from time import time
import traceback
import config
import bnw_core.base
import bnw_core.ensure_indexes
import bnw_xmpp.base
from bnw_core.bnw_mongo import open_db
from bnw_xmpp import bnw_component, xmpp_notifier

bnw_core.base.config.register(config)
application = service.Application("BnW")

open_db()

from twisted.internet import reactor
reactor.callWhenRunning(bnw_core.ensure_indexes.index)

# Set up XMPP component.
sm = component.buildServiceManager(
    config.srvc_name, config.srvc_pwd,
    ('tcp:'+config.xmpp_server))

# Turn on verbose mode.
bnw_component.LogService().setServiceParent(sm)

# Set up our service.
s = bnw_component.BnwService()
s.setServiceParent(sm)

bnw_xmpp.base.service.register(s)
bnw_core.base.notifiers.add(xmpp_notifier.XmppNotifier())

serviceCollection = service.IServiceCollection(application)
sm.setServiceParent(serviceCollection)

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
    internet.TCPServer(
        config.rpc_port, server.Site(s.getRPC()),
        interface="127.0.0.1").setServiceParent(serviceCollection)

if config.manhole:
    shell_factory = ShellFactory()
    shell_factory.password = config.manhole
    shell_tcp_server = internet.TCPServer(4040, shell_factory, interface="127.0.0.1")
    shell_tcp_server.setServiceParent(serviceCollection)

if config.webui_enabled:
    import bnw_web.site
    http_server = bnw_web.site.get_site()
    http_server.listen(config.webui_port, "127.0.0.1")

bnw_core.base.timertime = 0
def checkload(lasttime):
    currenttime = time()
    if lasttime is not None:
        bnw_core.base.timertime = currenttime - lasttime
    reactor.callLater(1, checkload, currenttime)
checkload(None)
