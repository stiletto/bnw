# coding: utf-8
import sys
import passwords
try:
    sys.setappdefaultencoding('utf-8')
except:
    sys=reload(sys)
    sys.setdefaultencoding('utf-8')
import os.path as path
root=path.abspath(path.dirname(__file__))
sys.path.append(root)
sys.path.insert(0,path.join(root,'mongo-async-python-driver'))
sys.path.insert(0,path.join(root,'tornado'))

from twisted.application import service,internet

from twisted.words.protocols.jabber import component

from twisted.web import resource, server, static, xmlrpc

import bnw_component

application = service.Application("example-echo")

# set up Jabber Component
sm = component.buildServiceManager('bnw.blasux.ru', passwords.bnw,
                    ("tcp:127.0.0.1:6591" ))


# Turn on verbose mode
bnw_component.LogService().setServiceParent(sm)

# set up our example Service
s = bnw_component.BnwService()
s.setServiceParent(sm)

serviceCollection = service.IServiceCollection(application)

internet.TCPServer(8081, server.Site(s.getResource()), interface="127.0.0.1"
                   ).setServiceParent(serviceCollection)
                   
sm.setServiceParent(serviceCollection)#application)

