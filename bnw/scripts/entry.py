#!/bin/echo tac is a python source file, but should be started via twistd


def _entrypoint(name):
    def entrypoint():
        import sys
        from os import path
        app = path.join(path.dirname(__file__),name)
        sys.argv.insert(1, app)
        sys.argv.insert(1, '-y')
        from twisted.scripts.twistd import run
        run()
    return entrypoint

instance = _entrypoint('instance.tac')
search = _entrypoint('search.tac')
