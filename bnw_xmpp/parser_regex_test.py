# -*- coding: utf-8 -*-
from parser_regex import *

if __name__=="__main__":
    # This is some sort of parser test.
    handlers = (
        (r'PING', 'ping'),
        (r'REGISTER (?P<name>\S+)','register'),
        (r'INTERFACE (?P<iface>\S+)','interface'),
        (r'D #(?P<message>.+)','delete'),
        (r'D L','delete',{'last':True}),
        (r'S','subscriptions'),
        (r'S @(?P<user>\S+)','subscribe'),
        (r'S \*(?P<tag>\S+)','subscribe'),
        (r'S !(?P<club>\S+)','subscribe'),
        (r'U @(?P<user>\S+)','unsubscribe'),
        (r'U \*(?P<tag>\S+)','unsubscribe'),
        (r'U !(?P<club>\S+)','unsubscribe'),
        (r'L @(?P<user>\S+)','not_implemented'),
        (r'HELP','help'),
        (r'LOGIN','login'),
        (r'ON','on'),
        (r'OFF','off'),
        (r'PM +@(?P<user>\S+) +(?P<text>.+)','pm'),
        (r'BL','not_implemented'),
        (r'BL .+','not_implemented'),
        (r'\? .+','not_implemented'),
        (r'#','feed'),
        (r'#\+','show'),
        (r'@(?P<user>\S+)','show'),
        (r'@(?P<user>\S+)','show'),
        (r'@(?P<user>\S+) \*(?P<tag>\S+)','show'),
        (r'\*(?P<tag>\S+)','show'),
        (r'!(?P<club>\S+)','show'),
        (r'#(?P<message>[0-9A-Za-z]+)','show'),
        (r'#(?P<message>[0-9A-Za-z]+)\+','show',{'replies':True}),
        (r'#(?P<message>[0-9A-Za-z]+) (?P<text>.+)','comment'),
        (r'#(?P<message>[0-9A-Za-z]+/[0-9A-Za-z]+) (?P<text>.+)','comment'),
        (r'! +#(?P<message>[0-9A-Za-z]+)(?: (?P<comment>.+))?','recommend'),
        (r'(?:(?P<tag1>[\*!]\S+)?(?: (?P<tag2>[\*!]\S+))?(?: (?P<tag3>[\*!]\S+))?(?: (?P<tag4>[\*!]\S+))?(?: (?P<tag5>[\*!]\S+))? )?(?P<text>.+)',
            'post'),
    )


    p=RegexParser(handlers,[])
    test="""
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
        def __init__(self,b):
            self.body=b
    for a in test.split('\n'):
        a=a.strip()
        if not a:
            continue
        msg=ShitMsg(a)
        print a,p.resolve(msg)
    print "Done ok."
else:
    raise Exception("Do not import this shit, just run it!")
