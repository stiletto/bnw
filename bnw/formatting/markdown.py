import re
import weakref
from re import compile as rec

from tornado.escape import _unicode, xhtml_escape, url_escape
from misaka import HtmlRenderer, Markdown
import misaka as m

from linkshit import LinkParser, _URL_RE
import linkshit_format

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
        for regexp, handler, _ in linkshit_format.linkhostings:
            m = regexp.match(url)
            if m:
                thumb = handler(m.group, 's' if secure else '')
                thumbs.append((url, thumb))
                break
    return thumbs

bnwlinks_parser = LinkParser(types=linkshit_format.bnw_types)

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
        text = _unicode(xhtml_escape(text))
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


class MarkdownFormat(object):
    def format(self, raw, secure=False):
        raw = _unicode(raw)
        formatted_text = ignore_trailing_newlines(markdown_parser.render(raw))
        thumbs = get_thumbs(raw, secure)
        return formatted_text, thumbs
