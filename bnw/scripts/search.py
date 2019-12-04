import os
import sys
from twisted.application import internet, service
from twisted.web import server
import bnw.core.base
import bnw.core.bnw_mongo

from bnw.search.search_server import RPCSearch
import config


bnw.core.base.config.register(config)
bnw.core.bnw_mongo.open_db()

application = service.Application('BnW search service')
r = RPCSearch(config.search_db, config.search_language)
if isinstance(config.search_port, str) and ':' in config.search_port:
    search_host, search_port = config.search_port.rsplit(":", 1)
else:
    search_host, search_port = "127.0.0.1", config.search_port
search_service = internet.TCPServer(
    search_port, server.Site(r), interface=search_host)
search_service.setServiceParent(application)

def runintwistd():
    sys.argv.insert(1,__file__)
    sys.argv.insert(1,'-y')
    from twisted.scripts.twistd import run
