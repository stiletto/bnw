# coding: utf-8
import re
from linkshit.linkshit import linkparse, _URL_RE
from tornado.escape import _unicode,xhtml_escape,url_escape

linkhostings = [
    (ur'http://rghost.ru/([0-9]+)', lambda m: 'http://rghost.ru/%s/thumb.png' % (m(1),)),
    (ur'http://imgur.com/([A-Za-z0-9]+)', lambda m: 'http://i.imgur.com/%ss.png' % (m(1),)),
    (ur'http://ompldr.org/v([A-Za-z0-9]+)(/.+)?', lambda m: 'http://ompldr.org/t%s' % (m(1),)),
    (ur'http://2-ch.ru/([a-z]+)/src/([0-9]+).(png|gif|jpg)', lambda m: 'http://2-ch.ru/%s/thumb/%ss.%s' % (m(1),m(2),m(3))),
    (ur'http://(.+.(?:png|gif|jpg|jpeg))', lambda m: 'http://fuck.blasux.ru/thumb?img=%s' % (url_escape(m(0)),)),
]

linkhostings=[(re.compile('^'+k+'$'),v,k) for (k,v) in linkhostings]

def thumbify(text,permitted_protocols = ['http','https']):
    text = _unicode(xhtml_escape(text))
    texta = []
    thumbs = []
    for m in linkparse(text):
        if isinstance(m,tuple):
            if m[0]=='url':
                up = _URL_RE.match(m[2])
                url = up.group(1)
                proto = up.group(2)
                if proto not in permitted_protocols:
                    texta.append('%s<!-- proto! -->' % (m[1],))
                else:
                    if not proto:
                        url = "http://" + url
                    for lh in linkhostings:
                        m = lh[0].match(url)
                        if m:
                            thumb = lh[1](m.group)
                            thumbs.append((url,thumb))
                            break
                texta.append('<a href="%s">%s</a>' % (url,url))
            elif m[0]=='msg':
                texta.append('<a href="/p/%s">%s</a>' % (m[2].replace('/','#'),m[1]))
            elif m[0]=='user':
                texta.append('<a href="/u/%s">%s</a>' % (m[2],m[1]))
            else:
                texta.append('%s<!-- %s -->' % (m[1],m[0]))
        else:
            texta.append(m)
    return ''.join(texta), thumbs

def linkify(text):
    return thumbify(text)[0]
