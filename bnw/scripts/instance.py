import argparse
import logging
import os
import sys
import threading
import time
import traceback
import tornado

import bnw.core
from bnw.core.config import config, Config
import bnw.web.site

def log_reconfig(old, new):
    if not old.compare(new, 'loglevel'):
        logging.basicConfig(level=new.loglevel)

def config_handler(old, new):
    if not old.compare(new, 'webui_port'):
        site = bnw.web.get_site()
        

def entry():
    config.register_handler(log_reconfig)
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser('BnW xmpp and web service')
    parser.add_argument('config', metavar='CONFIG', help='Configuration file name', default='config.py')
    parser.add_argument('--pidfile', metavar='PIDFILE', help='Write pid to this file', default='')
    args = parser.parse_args()
    new_config = Config()
    if args.pidfile:
        try:
            f = open(args.pidfile, 'w')
            f.write(str(os.getpid()))
            f.close()
        except:
            logging.error("Failed to write PID to '%s': %s", args.pidfile, traceback.format_exc())
    execfile(args.config, {'logging':logging}, new_config)
    try:
        result = config.update_config(new_config)
    except:
        result = traceback.format_exc()
    if result:
        logging.error('Unable apply config file: %s', result)
        return

    def index_func():
        while True:
            lss = search
            lss.run_incremental_indexing()
            time.sleep(3600)

    indexer = threading.Thread(target=index_func, name='indexer')
    indexer.daemon = True
    indexer.start()
    while True:
        logging.info('Starting search server')
        search_server.serve_forever()

if __name__=="__main__":
    entry()

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
import bnw.core.base
import bnw.core.ensure_indexes
import bnw.xmpp.base
from bnw.core.bnw_mongo import open_db
from bnw.xmpp import bnw_component, xmpp_notifier

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
    import bnw.web.site
    http_server = bnw.web.site.get_site()
    http_server.listen(config.webui_port, "127.0.0.1")

bnw.core.base.timertime = 0
def checkload(lasttime):
    currenttime = time()
    if lasttime is not None:
        bnw.core.base.timertime = currenttime - lasttime
    reactor.callLater(1, checkload, currenttime)
checkload(None)

def runintwistd():
    sys.argv.insert(1,__file__)
    sys.argv.insert(1,'-y')
    from twisted.scripts.twistd import run
