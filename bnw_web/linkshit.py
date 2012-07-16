#
# Copyright 2012 Stiletto <blasux@blasux.ru>
#
# Licensed under the MIT License.
#
# coding: utf-8
import re


_URL_RE = re.compile(ur"""\b((?:([\w-]+):(/{1,3})|www[.])(?:(?:(?:[^\s&()]|&amp;|&quot;)*(?:[^!"#$%&'()*+,.:;<=>?@\[\]^`{|}~\s]))|(?:\((?:[^\s&()]|&amp;|&quot;)*\)))+)""")
_USER_RE = re.compile(ur"""(?:(?<=[\s\W])|^)@([0-9A-Za-z-]+)""")
_MSG_RE = re.compile(ur"""(?:(?<=[\s\W])|^)#([0-9A-Za-z]+(?:/[0-9A-Za-z]+)?)""")

def url_handler(match):
    return ('url',match.group(1))

def msg_handler(match):
    return ('msg',match.group(1))

def user_handler(match):
    return ('user',match.group(1))

shittypes = (
    ('url',  _URL_RE,  lambda m: (m.group(1),)),
    ('msg',  _MSG_RE,  lambda m: (m.group(1),)),
    ('user', _USER_RE, lambda m: (m.group(1),)),
)

class LinkParser(object):
    def __init__(self,types=shittypes):
        self.types = types

    def parse(self,text):
        pos = 0
        texlen = len(text)
        while pos<texlen:
            mins = texlen
            minm = None
            for typ,reg,handler in self.types:
                m = reg.search(text[pos:])
                if m is None:
                    continue
                s = m.start()
                if s<mins:
                    mins = s
                    minm = (m,typ, handler)
            if minm is None:
                yield text[pos:]
                return
            else:
                yield text[pos:pos+mins]
                yield (minm[1],minm[0].group(0))+minm[2](minm[0])
                pos = pos + minm[0].end()

_shitparser = LinkParser()
def linkparse(text):
    return _shitparser.parse(text)
