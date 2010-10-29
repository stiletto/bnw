#!/usr/bin/env python
# coding: utf-8

import bnw_shell
import txmongo
from txmongo import filter
from twisted.internet import defer, reactor
import bnw_core.bnw_objects
import bnw_xmpp
from bnw_core.base import get_db

@defer.inlineCallbacks
def example():
    for x in (yield bnw_core.bnw_objects.User.find()):
        print x
    
if __name__ == '__main__':
    example().addCallback(lambda ign: reactor.stop())
    reactor.run()
