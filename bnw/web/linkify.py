import re
from re import compile as rec

from tornado.escape import _unicode, xhtml_escape, url_escape
from misaka import HtmlRenderer, Markdown
import misaka as m

from bnw.web.linkshit import LinkParser, shittypes
from bnw.web.linkshit import _URL_RE, _USER_RE, _MSG_RE


#: Displaying thumbs allowed for the following hostings:
linkhostings = [
    (ur'(?i)http://rghost.(net|ru)/([0-9]+)', lambda m,s: 'http%s://rghost.%s/%s/thumb.png' % (s,m(1),m(2))),
    (ur'(?i)https?://imgur.com/([A-Za-z0-9]+)', lambda m,s: 'http%s://i.imgur.com/%ss.png' % (s,m(1),)),
    (ur'http://(2ch.hk|2ch.pm|2ch.re|2ch.tf|2ch.wf|2ch.yt|2-ch.so)/([a-z]+)/src/([0-9]+).(png|gif|jpg)', lambda m,s: 'http%s://%s/%s/thumb/%ss.gif' % (s,m(1),m(2),m(3))),
    (ur'https?://(?:www\.)?youtube.com/watch\?(?:.+&)?v\=([A-Z0-9a-z_-]+)(?:&.+)?', lambda m,s: 'http%s://img.youtube.com/vi/%s/default.jpg' % (s,m(1))),
    (ur'(?i)https?://upload.wikimedia.org/wikipedia/commons/([0-9]{1}\/[A-Za-z0-9]+)/([A-Za-z0-9_.]+)', lambda m,s: 'http%s://upload.wikimedia.org/wikipedia/commons/thumb/%s/%s/256px-%s' % (s,m(1),m(2),m(2))),
    (ur'(?i)https?://(.+.(?:png|gif|jpg|jpeg))', lambda m,s: 'http%s://bnw-thumb.r.worldssl.net/thumb?img=%s' % (s,url_escape(m(0)),)),
]
linkhostings = [(re.compile('^' + k + '$'), v, k) for (k, v) in linkhostings]


def thumbify(text, format='markdown', secure=False):
    """Format text and generate thumbs using available formatters.

    :param format: default: 'markdown'. Specify text formatter.
                   Variants: 'moinmoin', 'markdown' or None,
                   which fallbacks to markdown.

    Return: (formatted_text, thumbs)
    Thumbs: list of (original_file_url, thumb_url)
    """
    if format == 'moinmoin':
        return moinmoin(text, secure)
    else:
        return markdown(text, secure)


def linkify(text, format='markdown'):
    """Only do text formatting. See :py:meth:`thumbify`."""
    return thumbify(text, format=format)[0]


###
# New markdown formatter with some custom render rules.
###


def ignore_trailing_newlines(text):
    return text.rstrip('\n')


def msg_url(match):
    text = match.group(0)
    url_part = match.group(1).replace('/', '#')
    return '[{0}](/p/{1})'.format(text, url_part)


def get_thumbs(raw, secure=False):
    # Don't forget about escaping
    text = xhtml_escape(raw)
    thumbs = []
    for match in _URL_RE.finditer(text):
        url = match.group(1)
        for regexp, handler, _ in linkhostings:
            m = regexp.match(url)
            if m:
                thumb = handler(m.group, 's' if secure else '')
                thumbs.append((url, thumb))
                break
    return thumbs

bnwlinks_types = (
    ('msg', _MSG_RE, lambda m: (m.group(1),)),
    ('user', _USER_RE, lambda m: (m.group(1),)),
)

bnwlinks_parser = LinkParser(types=bnwlinks_types)

def bnwlinks(text):
    texta = []
    for m in bnwlinks_parser.parse(text):
        if isinstance(m, tuple):
            if m[0] == 'msg':
                texta.append('<a href="/p/%s">%s</a>' % (m[2].replace('/', '#'), m[1]))
            elif m[0] == 'user':
                texta.append('<a href="/u/%s">%s</a>' % (m[2], m[1]))
            else:
                texta.append('%s<!-- %s -->' % (m[1], m[0]))
        else:
            texta.append(m)
    return ''.join(texta)

blockquote_crap = re.compile(ur'(^|\n)\s*>.+(?=\n[^>\n])')

class BnwRenderer(HtmlRenderer):
    """Wrapper around default misaka's renderer."""

    def preprocess(self, text):
        """Apply some additional BnW's rules."""
        #text = _USER_RE.sub('[\g<0>](/u/\g<1>)', text)
        #text = _MSG_RE.sub(msg_url, text)
        text = blockquote_crap.sub('\g<0>\n', text) # fuck you, kagami
        return text

    def normal_text(self, text):
        return bnwlinks(text)

    def block_quote(self, text):
        """Do some wakaba-like fixes.
        Through wakaba parses block quotes in something different
        manner (they are not stick together).
        """
        # TODO: Should we be more wakabic?
        text = ignore_trailing_newlines(text)
        return '<blockquote>{0}</blockquote>\n'.format(text)

    def header(self, text, level):
        """Fix odd newlines in default header render."""
        return '<h{0}>{1}</h{0}>'.format(level, text)

    def paragraph(self, text):
        """Use just newlines instead of paragraphs
        (becase we already in the <pre> tag).
        """
        return '<p>'+ text.replace('\n','<br/>') + '</p>'

    def image(self, link, title, alt_text):
        """Don't allow images (they could be big).
        Use simple links intead.
        """
        # Don't forget about escaping
        return '<a href="{0}">{0}</a>'.format(xhtml_escape(link))

    def block_code(self, code, language):
        # Don't forget about escaping
        code = ignore_trailing_newlines(xhtml_escape(code))
        if language:
            language = xhtml_escape(language)
            klass = ' class="language-{0}"'.format(language)
        else:
            klass = ''
        return '<pre><code{0}>{1}</code></pre>\n'.format(klass, code)


# Don't touch HTML_ESCAPE flag!
renderer = BnwRenderer(m.HTML_ESCAPE | m.HTML_SAFELINK)
markdown_parser = Markdown(
    renderer,
    m.EXT_NO_INTRA_EMPHASIS | m.EXT_AUTOLINK | m.EXT_FENCED_CODE)


def markdown(raw, secure=False):
    raw = _unicode(raw)
    formatted_text = ignore_trailing_newlines(markdown_parser.render(raw))
    thumbs = get_thumbs(raw, secure)
    return formatted_text, thumbs


###
# Simple MoinMoin-like formatter. Legacy.
###


moin_types = (
    ("emph", rec(ur'(?<!:)//'), lambda m: ()),
    ("strong", rec(ur'\*\*'), lambda m: ()),
    ("namedlink", rec(ur'''\[\[\s*(?P<link_target>.+?)\s*[|]\s*(?P<link_text>.+?)\s*]]'''), lambda m: (m.group('link_target'),m.group('link_text'))),
    ("source", rec(ur'''{{{(?:#!(\w+)\s+)?(.*?)}}}''', re.MULTILINE|re.DOTALL), lambda m: (m.group(1),m.group(2))),
)


formatting_tags = {
    'emph': ('<i>', '</i>'),
    'strong': ('<b>', '</b>'),
}


moin_parser = LinkParser(types=moin_types + shittypes)
parser = LinkParser(types=moin_types + shittypes)


def moinmoin(text, secure=False):
    text = _unicode(xhtml_escape(text))
    permitted_protocols = ["http", "https", "ftp", "git",
                           "gopher", "magnet", "mailto", "xmpp"]
    texta = []
    thumbs = []
    stack = []
    instrong = False
    inemph = False
    for m in parser.parse(text):
        if isinstance(m, tuple):
            if m[0] in ('url', 'namedlink'):
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
                if proto and proto not in permitted_protocols:
                    texta.append('%s<!-- proto! -->' % (m[1],))
                else:
                    if not proto:
                        url = "http://" + url
                    for lh in linkhostings:
                        mn = lh[0].match(url)
                        if mn:
                            thumb = lh[1](mn.group, 's' if secure else '')
                            thumbs.append((url, thumb))
                            break
                    texta.append('<a href="%s">%s</a>' % (url, m[3]))
            elif m[0] in formatting_tags.keys():
                tag = formatting_tags[m[0]]
                if not m[0] in stack:
                    texta.append(tag[0])
                    stack.insert(0, m[0])
                else:
                    tp = stack.index(m[0])
                    for uptag in stack[:tp + 1]:
                        texta.append(formatting_tags[uptag][1])
                    for uptag in reversed(stack[:tp]):
                        texta.append(formatting_tags[uptag][0])
                    del stack[tp]
            elif m[0] == 'msg':
                texta.append(
                    '<a href="/p/%s">%s</a>' % (m[2].replace('/', '#'), m[1]))
            elif m[0] == 'user':
                texta.append('<a href="/u/%s">%s</a>' % (m[2], m[1]))
            elif m[0] == 'source':
                cs = (' class="language-' + m[2] + '"') if m[2] else ''
                texta.append('<pre><code%s>%s</code></pre>' % (cs, m[3]))
            else:
                texta.append('%s<!-- %s -->' % (m[1], m[0]))
        else:
            texta.append(m)
    for i in stack:
        texta.append(formatting_tags[i][1])
    return ''.join(texta), thumbs
