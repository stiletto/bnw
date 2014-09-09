import re
from re import compile as rec

import linkshit
import linkshit_format

moin_types = linkshit_format.bnw_autolinks + (
    ("emph", rec(ur'(?<!:)//'), lambda m: ()),
    ("strong", rec(ur'\*\*'), lambda m: ()),
    ("namedlink", rec(ur'''\[\[\s*(?P<link_target>.+?)\s*[|]\s*(?P<link_text>.+?)\s*]]'''), lambda m: (m.group('link_target'),m.group('link_text'))),
    ("source", rec(ur'''{{{(?:#!([0-9A-Za-z]+)\s+)?(.*?)}}}''', re.MULTILINE|re.DOTALL), lambda m: (m.group(1),m.group(2))),
)


formatting_tags = {
    'emph': ('<i>', '</i>'),
    'strong': ('<b>', '</b>'),
}

#moin_parser = LinkParser(types=moin_types + shittypes)
#plain_parser = LinkParser(types=shittypes)

class MoinMoinFormat(linkshit_format.LinkShitFormat):
    def __init__(self):
        parser = linkshit.LinkParser(types=moin_types)
        super(MoinMoinFormat, self).__init__(parser, formatting_tags)

    def format_source(self, m, secure):
        cs = (' class="language-' + m[2] + '"') if m[2] else ''
        return ('<pre><code%s>%s</code></pre>' % (cs, m[3])), None
