# coding: utf-8
import re
from re import compile as rec
from bnw_web.linkshit import LinkParser, _URL_RE, shittypes
from tornado.escape import _unicode,xhtml_escape,url_escape

linkhostings = [
    (ur'(?i)http://rghost.ru/([0-9]+)', lambda m: 'http://rghost.ru/%s/thumb.png' % (m(1),)),
    (ur'(?i)http://imgur.com/([A-Za-z0-9]+)', lambda m: 'http://i.imgur.com/%ss.png' % (m(1),)),
    (ur'http://ompldr.org/v([A-Za-z0-9]+)(/.+)?', lambda m: 'http://ompldr.org/t%s' % (m(1),)),
    (ur'http://2-ch.ru/([a-z]+)/src/([0-9]+).(png|gif|jpg)', lambda m: 'http://2-ch.ru/%s/thumb/%ss.%s' % (m(1),m(2),m(3))),
    (ur'(?i)http://(.+.(?:png|gif|jpg|jpeg))', lambda m: 'http://fuck.blasux.ru/thumb?img=%s' % (url_escape(m(0)),)),
]

linkhostings=[(re.compile('^'+k+'$'),v,k) for (k,v) in linkhostings]

bnwtypes = (
    ("emph", rec(ur'(?<!:)//'), lambda m: ()),
    ("strong", rec(ur'\*\*'), lambda m: ()),
    ("namedlink", rec(ur'''\[\[\s*(?P<link_target>.+?)\s*[|]\s*(?P<link_text>.+?)\s*]]'''), lambda m: (m.group('link_target'),m.group('link_text'))),
)
formatting_tags = {
    'emph': ('<i>','</i>'),
    'strong': ('<b>','</b>'),
}

parser = LinkParser(types=bnwtypes+shittypes)

def thumbify(text, permitted_protocols=None):
    text = _unicode(xhtml_escape(text))
    if not permitted_protocols:
        permitted_protocols = ["http", "https"]
    texta = []
    thumbs = []
    stack = []
    instrong = False
    inemph = False
    for m in parser.parse(text):
        if isinstance(m,tuple):
            if m[0] in ('url','namedlink'):
                # TODO: Move checking for permitted protocols
                # in linkshit module? Matching twice is bad.
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
                            thumb = lh[1](mn.group)
                            thumbs.append((url,thumb))
                            break
                    texta.append('<a href="%s">%s</a>' % (url, m[3]))
            elif m[0] in formatting_tags.keys():
                tag = formatting_tags[m[0]]
                if not m[0] in stack:
                    texta.append(tag[0])
                    stack.insert(0,m[0])
                else:
                    tp = stack.index(m[0])
                    for uptag in stack[:tp+1]:
                        texta.append(formatting_tags[uptag][1])
                    for uptag in reversed(stack[:tp]):
                        texta.append(formatting_tags[uptag][0])
                    del stack[tp]
            elif m[0]=='msg':
                texta.append('<a href="/p/%s">%s</a>' % (m[2].replace('/','#'),m[1]))
            elif m[0]=='user':
                texta.append('<a href="/u/%s">%s</a>' % (m[2],m[1]))
            else:
                texta.append('%s<!-- %s -->' % (m[1],m[0]))
        else:
            texta.append(m)
    for i in stack:
        texta.append(formatting_tags[i][1])
    return ''.join(texta), thumbs

def linkify(text):
    return thumbify(text)[0]
