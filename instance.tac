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
import config
import bnw_core.base
import bnw_xmpp.base
from bnw_xmpp import bnw_component, xmpp_notifier

bnw_core.base.config.register(config)
application = service.Application("BnW")

# Set up XMPP component.
sm = component.buildServiceManager(
    config.srvc_name, config.srvc_pwd,
    ('tcp:127.0.0.1:%i' % config.srvc_port))

# Turn on verbose mode.
bnw_component.LogService().setServiceParent(sm)

# Set up our service.
s = bnw_component.BnwService()
s.setServiceParent(sm)

bnw_xmpp.base.service.register(s)
bnw_core.base.notifiers.add(xmpp_notifier.XmppNotifier())

serviceCollection = service.IServiceCollection(application)
sm.setServiceParent(serviceCollection)

if config.rpc_enabled:
    internet.TCPServer(
        config.rpc_port, server.Site(s.getRPC()),
        interface="127.0.0.1").setServiceParent(serviceCollection)

if config.webui_enabled:
    import bnw_web.site
    http_server = bnw_web.site.get_site()
    http_server.listen(config.webui_port, "127.0.0.1")
