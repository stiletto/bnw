import re
from re import compile as rec

from tornado.escape import _unicode, xhtml_escape, url_escape

from linkshit import LinkParser, clip_long_url
from linkshit import _URL_RE, _MSG_RE
from libthumbor import CryptoURL

from bnw.core.base import config
from bnw.handlers.base import USER_RE

_USER_RE = re.compile(ur"""(?:(?<=[\s\W])|^)@(%s)""" % USER_RE)

bnw_types = (
    ('msg', _MSG_RE, lambda m: (m.group(1),)),
    ('user', _USER_RE, lambda m: (m.group(1),)),
)

bnw_autolinks = (
    ('url', _URL_RE, lambda m: (m.group(1), clip_long_url(m))),
) + bnw_types

thumbor = None

def own_thumbnail(m, s):
    global thumbor

    proto = 'http%s' % s
    thumbor_base = config.thumbor % { 'proto': proto }

    if thumbor is None:
        thumbor = CryptoURL(key=config.thumbor_key)
    return thumbor_base+thumbor.generate(image_url=m(0), **config.thumbor_pars)

#: Displaying thumbs allowed for the following hostings:
linkhostings = [
    (ur'(?i)http://rghost.(net|ru)/([0-9]+)', lambda m,s: 'http%s://rghost.%s/%s/thumb.png' % (s,m(1),m(2))),
    (ur'(?i)https?://(?:i\.)?imgur.com/([A-Za-z0-9]+)(?:\..*)?', lambda m,s: 'http%s://i.imgur.com/%ss.png' % (s,m(1),)),
    (ur'http://(2ch.hk|2ch.pm|2ch.re|2ch.tf|2ch.wf|2ch.yt|2-ch.so)/([a-z]+)/src/([0-9]+).(png|gif|jpg)', lambda m,s: 'http%s://%s/%s/thumb/%ss.gif' % (s,m(1),m(2),m(3))),
    (ur'https?://(?:www\.)?youtube.com/watch\?(?:.+&)?v\=([A-Z0-9a-z_-]+)(?:&.+)?', lambda m,s: 'http%s://img.youtube.com/vi/%s/default.jpg' % (s,m(1))),
    (ur'(?i)https?://upload.wikimedia.org/wikipedia/commons/([0-9]{1}\/[A-Za-z0-9]+)/([A-Za-z0-9_.]+)', lambda m,s: 'http%s://upload.wikimedia.org/wikipedia/commons/thumb/%s/%s/256px-%s' % (s,m(1),m(2),m(2))),
    (ur'(?i)https?://(.+.(?:png|gif|jpg|jpeg))', own_thumbnail),
]
linkhostings = [(re.compile('^' + k + '$'), v, k) for (k, v) in linkhostings]


class LinkShitFormat(object):
    permitted_protocols = ["http", "https", "ftp", "git",
                           "gopher", "magnet", "mailto", "xmpp"]

    def __init__(self, parser, formatting_tags=None):
        self.parser = parser
        self.formatting_tags = formatting_tags or {}
        self._formatfuncs = {}
        for x in dir(self):
            if x.startswith('format_'):
                self._formatfuncs[x[7:]] = getattr(self, x)

    def format(self, text, secure=False):
        #def linkshit_format(text, secure=False, parser=moin_parser):
        text = _unicode(xhtml_escape(text))
        out = []
        thumbs = []
        stack = []
        instrong = False
        inemph = False
        self.formatting_tags.keys()
        for m in self.parser.parse(text):
            if isinstance(m, tuple):
                if m[0] in self._formatfuncs:
                    new_html, new_thumb = self._formatfuncs[m[0]](m, secure)
                    if new_html:
                        out.append(new_html)
                    if new_thumb:
                        thumbs.append(new_thumb)
                elif m[0] in self.formatting_tags:
                    tag = self.formatting_tags[m[0]]
                    if not m[0] in stack:
                        out.append(tag[0])
                        stack.insert(0, m[0])
                    else:
                        tp = stack.index(m[0])
                        for uptag in stack[:tp + 1]:
                            out.append(self.formatting_tags[uptag][1])
                        for uptag in reversed(stack[:tp]):
                            out.append(self.formatting_tags[uptag][0])
                        del stack[tp]
                else:
                    out.append('%s<!-- %s -->' % (m[1], m[0]))
            else:
                out.append(m)
        for i in stack:
            out.append(self.formatting_tags[i][1])
        return '<div class="pwls">'+''.join(out)+'</div>', thumbs

    def format_url(self, m, secure):
        # TODO: Move checking for permitted protocols
        # in linkshit module? Matching twice is bad.
        if m[0] == 'namedlink':
            up = m[2].split(':', 1)
            proto = up[0] if len(up) == 2 else None
            url = m[2]
        else:
            up = _URL_RE.match(m[2])
            url = m[2] if up is None else up.group(1)
            proto = None if up is None else up.group(2)
        if proto and proto not in self.permitted_protocols:
            return ('%s<!-- proto! -->' % (m[1],)), None
        if not proto:
            url = "http://" + url
        result = '<a href="%s">%s</a>' % (url, m[3])
        for lh in linkhostings:
            mn = lh[0].match(url)
            if mn:
                thumb = lh[1](mn.group, 's' if secure else '')
                return result, (url, thumb)
        return result, None

    def format_namedlink(self, m, secure):
        return self.format_url(m, secure)

    def format_msg(self, m, secure):
        return ('<a href="/p/%s">%s</a>' % (m[2].replace('/', '#'), m[1])), None

    def format_user(self, m, secure):
        return ('<a href="/u/%s">%s</a>' % (m[2], m[1])), None
