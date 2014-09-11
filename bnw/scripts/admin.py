import os
import sys
import argparse
import time
from twisted.internet import defer
from twisted.python import log
import bnw.core.base
import bnw.core.bnw_mongo
import collections

class LRU(object):
    def __init__(self, size=0):
        self.size = size
        self.items = collections.OrderedDict()
    def __getitem__(self, key):
        value = self.items.pop(key)
        self.items[key] = value
        return value
    def __setitem__(self, key, value):
        try:
            self.cache.pop(key)
        except KeyError:
            if len(self.items) >= self.size:
                self.items.popitem(last=False)
        self.items[key] = value

def defer_sleep(reactor, time):
    d = defer.Deferred()
    reactor.callLater(time, d.callback, None)
    return d

@defer.inlineCallbacks
def action_rerender(reactor, args):
    from bnw.core import bnw_objects as objs
    from bnw.core.post import renderPostOrComment
    counts = ((yield objs.Message.count()), (yield objs.Comment.count()))
    print counts
    log.msg('There are %d messages and %d comments.' % counts)
    for tname, t, tcnt in [('message', objs.Message, counts[0]), ('comment', objs.Comment, counts[1])]:
        log.msg('Processing %ss' % (tname,))
        cnt = 0
        while True:
            messages = list((yield t.find({}, limit=500, skip=cnt)))
            if not messages:
                log.msg('Done processing %ss.' % (tname,))
                break
            for message in messages:
                html = renderPostOrComment(message['text'], message.get('format'))
                yield t.mupdate({'_id': message['_id']}, {'$set':{'html': html}})
            cnt += len(messages)
            log.msg('(%d/%d) %ss processed.' % (cnt, tcnt, tname))
            #yield defer_sleep(reactor, 0.5)

def twistedrun(reactor):
    parser = argparse.ArgumentParser(description='BnW admin-tasks.')
    parser.add_argument('--rerender', dest='action', action='store_const',
                   const=action_rerender, default=None,
                   help='regenerate HTML for all messages and comments')
    args = parser.parse_args()
    if args.action is None:
        parser.print_help()
        reactor.stop()
    else:
        def errdie(*args, **kwargs):
            from twisted.python import log
            log.startLogging(sys.stderr)
            log.err(*args, **kwargs)
            reactor.stop()
        args.action(reactor, args).addCallbacks(lambda d: reactor.stop, errdie)

def main():
    import config

    import tornado.platform.twisted
    tornado.platform.twisted.install()

    bnw.core.base.config.register(config)
    bnw.core.bnw_mongo.open_db()

    log.startLogging(sys.stdout)
    from twisted.internet import reactor
    reactor.callWhenRunning(twistedrun, reactor)
    reactor.run()
if __name__=="__main__":
    main()
