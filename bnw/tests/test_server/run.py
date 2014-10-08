
if __name__=="__main__":
    import logging
    import os
    fr = os.fork()
    if fr < 0:
        logging.fatal('Unable to fork')
    elif fr == 0:
        from coverage import coverage
        #coverage.process_startup()
        cov = coverage(config_file=False, auto_data=True)
        cov.start()
        import atexit
        atexit.register(lambda: cov.stop())

        import sys
        from os import path
        sys.path.insert(0, path.dirname(__file__))
        while sys.argv:
            sys.argv.pop()
        sys.argv.append('bnw')
        sys.argv.append('-n')
        sys.argv.append('-l')
        sys.argv.append('test_server.log')
#        sys.argv.append('--pidfile=testinst.pid')
        from bnw.scripts.entry import instance
        instance()
    else:
        import sys
        from twisted.python import log
        log.startLogging(sys.stdout)

        from twisted.application import strports
        from twisted.python import usage
        from xmpp_tester import XmppTestServerFactory

        from tests import startTests

        from twisted.internet import reactor
        exitcode = 0
        def starter(f):
            d = startTests(f)
            def errback(x):
                print 'Test result:', x
                print 'Killing',fr
                os.kill(fr, 2)
                global exitcode
                exitcode = 1 if x else 0
                reactor.stop()
            d.addCallbacks(errback, errback)
        factory = XmppTestServerFactory(starter)
        svc = strports.listen('tcp:9781:interface=127.0.0.1', factory)
        #reactor.callWhenRunning(startTests, reactor, factory)
        reactor.run()
        sys.exit(exitcode)
        #from bnw.scripts
