# -*- coding: utf-8 -*-
from parser_regex import *

if __name__ == "__main__":
    # This is some sort of parser test.
    handlers = (
        (ur'PING', 'ping'),
        (ur'REGISTER (?P<name>\S+)', 'register'),
        (ur'INTERFACE (?P<iface>\S+)', 'interface'),
        (ur'D #(?P<message>.+)', 'delete'),
        (ur'D L', 'delete', {'last': True}),
        (ur'S', 'subscriptions'),
        (ur'S @(?P<user>\S+)', 'subscribe'),
        (ur'S \*(?P<tag>\S+)', 'subscribe'),
        (ur'S !(?P<club>\S+)', 'subscribe'),
        (ur'U @(?P<user>\S+)', 'unsubscribe'),
        (ur'U \*(?P<tag>\S+)', 'unsubscribe'),
        (ur'U !(?P<club>\S+)', 'unsubscribe'),
        (ur'L @(?P<user>\S+)', 'not_implemented'),
        (ur'HELP', 'help'),
        (ur'LOGIN', 'login'),
        (ur'ON', 'on'),
        (ur'OFF', 'off'),
        (ur'PM +@(?P<user>\S+)\s+(?P<text>.+)', 'pm'),
        (ur'BL', 'not_implemented'),
        (ur'BL .+', 'not_implemented'),
        (ur'\? .+', 'not_implemented'),
        (ur'#', 'feed'),
        (ur'#\+', 'show'),
        (ur'@(?P<user>\S+)', 'show'),
        (ur'@(?P<user>\S+)', 'show'),
        (ur'@(?P<user>\S+) \*(?P<tag>\S+)', 'show'),
        (ur'\*(?P<tag>\S+)', 'show'),
        (ur'!(?P<club>\S+)', 'show'),
        (ur'#(?P<message>[0-9A-Za-z]+)', 'show'),
        (ur'#(?P<message>[0-9A-Za-z]+)\+', 'show', {'replies': True}),
        (ur'#(?P<message>[0-9A-Za-z]+) (?P<text>.+)', 'comment'),
        (ur'#(?P<message>[0-9A-Za-z]+/[0-9A-Za-z]+) (?P<text>.+)', 'comment'),
        (ur'! +#(?P<message>[0-9A-Za-z]+)(?: (?P<comment>.+))?', 'recommend'),
        (ur'(?:(?P<tag1>[\*!]\S+)?(?: (?P<tag2>[\*!]\S+))?(?: (?P<tag3>[\*!]\S+))?(?: (?P<tag4>[\*!]\S+))?(?: (?P<tag5>[\*!]\S+))? )?(?P<text>.+)',
            'post'),
    )

    p = RegexParser(handlers, [])
    test = """
        *tagname Blah-blah-blah
        #1234 Blah-blah-blah
        #1234/5 Blah
        ! #1234

        #
        #+
        #1234
        #1234+
        @username
        @username+
        @username *tag
        *tag
        ? blah
        ? @username blah
        D #123
        D L
        S
        S #123
        S @username
        L @username
        U #123
        U @username
        BL
        BL @username
        BL *tag
        PM @username text
        ON
        OFF
        VCARD
        PING"""

    class ShitMsg(object):
        def __init__(self, b):
            self.body = b
    for a in test.split('\n'):
        a = a.strip()
        if not a:
            continue
        msg = ShitMsg(a)
        print a, p.resolve(msg)
    print "Done ok."
else:
    raise Exception("Do not import this shit, just run it!")
