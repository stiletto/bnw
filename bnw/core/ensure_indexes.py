#!/usr/bin/env python

try:
    from bnw.core import bnw_objects as objs
except ImportError:
    pass


def index():
    for name in dir(objs):
        cls = getattr(objs, name)
        if (isinstance(cls, type) and issubclass(cls, objs.MongoObject) and
                cls is not objs.MongoObject):
                print '---', name
                cls.ensure_indexes()
    print 'Indexes updated.'


if __name__ == '__main__':
    import sys
    import os.path
    root = os.path.join(os.path.dirname(__file__), '..')
    sys.path.insert(0, os.path.abspath(root))
    from twisted.internet import reactor
    import bnw.core.base
    from bnw.core import bnw_objects as objs
    import config

    bnw.core.base.config.register(config)
    index().addCallback(lambda ign: reactor.stop())
    reactor.run()
