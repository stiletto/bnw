#!/bin/echo tac is a python source file, but should be started via twistd
# coding: utf-8
import sys
import config
try:
    sys.setappdefaultencoding('utf-8')
except:
    sys=reload(sys)
    sys.setdefaultencoding('utf-8')
import os.path as path
root=path.abspath(path.dirname(__file__))
sys.path.append(root)
sys.path.insert(0,path.join(root,'txWebSocket'))


if True or config.webui_enabled:
    import tornado.platform.twisted
    tornado.platform.twisted.install()

import bnw_core.base
bnw_core.base.config.register(config)

from twisted.application import service,internet
from twisted.words.protocols.jabber import component
from twisted.web import resource, server, static, xmlrpc


from bnw_xmpp import bnw_component

application = service.Application("example-echo")

# set up Jabber Component
sm = component.buildServiceManager(config.srvc_name, config.srvc_pwd,
                    ('tcp:127.0.0.1:' + str(config.srvc_port) ))


# Turn on verbose mode
bnw_component.LogService().setServiceParent(sm)

# set up our example Service
s = bnw_component.BnwService()
s.setServiceParent(sm)

import bnw_xmpp.base
import bnw_xmpp.xmpp_notifier
bnw_xmpp.base.service.register(s)
bnw_core.base.notifiers.add(bnw_xmpp.xmpp_notifier.XmppNotifier())


serviceCollection = service.IServiceCollection(application)

sm.setServiceParent(serviceCollection)

if config.fuck_enabled:
    internet.TCPServer(config.fuck_port, server.Site(s.getResource()), interface="127.0.0.1"
                       ).setServiceParent(serviceCollection)

if config.webui_enabled:
    import bnw_web.site
    #import bnw_web.web_notifier
    http_server = bnw_web.site.get_site()
    http_server.listen(config.webui_port,"127.0.0.1")
    #bnw_core.base.notifiers.add(bnw_web.web_notifier.WebNotifier())
    #internet.TCPServer(config.webui_port, bnw_web.site.get_site(), interface="127.0.0.1"
    #                   ).setServiceParent(serviceCollection)                   
    #sm.setServiceParent(serviceCollection)
