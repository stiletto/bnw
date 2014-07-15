import argparse
import logging
import os
import sys
import threading
import time
import traceback
from SimpleXMLRPCServer import SimpleXMLRPCServer

import bnw.core
from bnw.search.search_server import RPCSearch
from bnw.core.config import config, Config

search = None
search_server = None
def search_reconfig(old, new):
    global search, search_server
    if not old.compare(new, 'search_db','search_language'):
        logging.info('Reconfiguring search: %s, %s', new.search_db, new.search_language)
        search = RPCSearch(new.search_db, new.search_language)
    if not old.compare(new, 'search_port'):
        logging.info('Reconfiguring search server: port %d', new.search_port)
        if search_server:
            logging.info('Shutting down previous instance of search server')
            search_server.shutdown()
        search_server = SimpleXMLRPCServer(("localhost", new.search_port), allow_none=True, encoding='utf-8')
        search_server.register_introspection_functions()
        search_server.register_function(search.xmlrpc_search, 'search')

def log_reconfig(old, new):
    if not old.compare(new, 'loglevel'):
        logging.basicConfig(level=new.loglevel)

def entry():
    config.register_handler(log_reconfig)
    logging.basicConfig(level=logging.INFO)
    config.register_handler(search_reconfig)
    parser = argparse.ArgumentParser('BnW search service')
    parser.add_argument('config', metavar='CONFIG', help='Configuration file name', default='config.py')
    args = parser.parse_args()
    new_config = Config()
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
