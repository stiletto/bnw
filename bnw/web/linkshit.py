#
# Copyright 2012 Stiletto <blasux@blasux.ru>
#
# Licensed under the MIT License.
#

import re
from bnw.handlers.base import USER_RE


_URL_RE = re.compile(ur"""\b((?:([\w-]+):(/{1,3})|www[.])(?:(?:(?:[^\s&()]|&amp;|&quot;)*(?:[^!"#$%&'()*+,.:;<=>?@\[\]^`{|}~\s]))|(?:\((?:[^\s&()]|&amp;|&quot;)*\)))+)""")
_USER_RE = re.compile(ur"""(?:(?<=[\s\W])|^)@(%s)""" % USER_RE)
_MSG_RE = re.compile(ur"""(?:(?<=[\s\W])|^)#([0-9A-Za-z]+(?:/[0-9A-Za-z]+)?)""")

shittypes = (
    ('url', _URL_RE, lambda m: (m.group(1), clip_long_url(m))),
    ('msg', _MSG_RE, lambda m: (m.group(1),)),
    ('user', _USER_RE, lambda m: (m.group(1),)),
)


def clip_long_url(m):
    """Clip long urls."""
    # It may be done much better.
    url = m.group(1)
    if len(url) > 55:
        url = url[:40] + "....." + url[-10:]
    return url


class LinkParser(object):
    def __init__(self, types=shittypes):
        self.types = types

    def parse(self, text):
        # Who the fuck write this piece of shit?
        # TODO: Refactor this shit.
        pos = 0
        texlen = len(text)
        while pos < texlen:
            mins = texlen
            minm = None
            for typ, reg, handler in self.types:
                m = reg.search(text[pos:])
                if m is None:
                    continue
                s = m.start()
                if s < mins:
                    mins = s
                    minm = (typ, m, handler)
            if not minm:
                yield text[pos:]
                return
            else:
                # TODO: Fix first empty value.
                yield text[pos:pos + mins]
                yield ((minm[0], minm[1].group(0)) + minm[2](minm[1]))
                pos = pos + minm[1].end()

_shitparser = LinkParser()


def linkparse(text):
    return _shitparser.parse(text)
