import linkshit
import linkshit_format

bnw_autolinks_noclip = (
    ('url', linkshit._URL_RE, lambda m: (m.group(1), m.group(1))),
) + linkshit_format.bnw_types

class PlainTextFormat(linkshit_format.LinkShitFormat):
    def __init__(self):
        parser = linkshit.LinkParser(types=bnw_autolinks_noclip)
        super(PlainTextFormat, self).__init__(parser)
