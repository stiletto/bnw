# coding: utf-8
import re
from re import compile as rec
from linkshit.linkshit import LinkParser, _URL_RE, shittypes
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
    ("namedlink", rec(ur'''\[\[\s*(?P<link_target>.+?)\s*([|]\s*(?P<link_text>.+?)\s*)?]]'''), lambda m: (m.group('link_target'),m.group('link_text'))),
)
formatting_tags = {
    'emph': ('<i>','</i>'),
    'strong': ('<b>','</b>'),
}

parser = LinkParser(types=bnwtypes+shittypes)

def thumbify(text,permitted_protocols = ['http','https']):
    text = _unicode(xhtml_escape(text))
    texta = []
    thumbs = []
    stack = []
    instrong = False
    inemph = False
    for m in parser.parse(text):
        if isinstance(m,tuple):
            if m[0] in ('url','namedlink'):
                print m
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
                link_text = m[3] if m[0]=='namedlink' else url
                texta.append('<a href="%s">%s</a>' % (url,link_text))
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

if __name__=="__main__":
    txs = (
	('''test //test test// test **test test** test''', 
	    'test <i>test test</i> test <b>test test</b> test'),
	('''test //test **test// test** test''',
	    'test <i>test <b>test</b></i><b> test</b> test'),
	(u'''Test *жирный* **жирный** ***жирный*** //курсив **жирный курсив**//''',
	    u'Test *жирный* <b>жирный</b> <b>*жирный</b>* <i>курсив <b>жирный курсив</b></i>'),
	('**test',
	    '<b>test</b>'),
	(u'''Обычный Советский Дурдом: http://allin777.livejournal.com/152675.html
[[ http://allin777.livejournal.com/152675.html|Обычный Советский Дурдом]]
"ИЗ РЕЧИ НИКОЛАЯ ЕЖОВА НА ПЛЕНУМЕ ЦК ВКП(б)
1 марта 1937 г.
ЕЖОВ. #ABCDEF Здесь заодно, товарищи разрешите сказать о таких умонастроениях, таких некоторых хозяйственников''',
	    u'''Обычный Советский Дурдом: <a href="http://allin777.livejournal.com/152675.html">http://allin777.livejournal.com/152675.html</a>
<a href="http://allin777.livejournal.com/152675.html">Обычный Советский Дурдом</a>
&quot;ИЗ РЕЧИ НИКОЛАЯ ЕЖОВА НА ПЛЕНУМЕ ЦК ВКП(б)
1 марта 1937 г.
ЕЖОВ. <a href="/p/ABCDEF">#ABCDEF</a> Здесь заодно, товарищи разрешите сказать о таких умонастроениях, таких некоторых хозяйственников'''),
        (u'''Wiki-разметка для ссылок (я про [[URL | text]] сейчас), как по мне, выглядит убого. Может, конвертировать её в что-то типа примечаний[1] или сносок[2]?
 1. http://dic.academic.ru/dic.nsf/ushakov/973938
 2. https://ru.wikipedia.org/wiki/Сноска''',
            u'''Wiki-разметка для ссылок (я про <a href="http://URL">text</a> сейчас), как по мне, выглядит убого. Может, конвертировать её в что-то типа примечаний[1] или сносок[2]?
 1. <a href="http://dic.academic.ru/dic.nsf/ushakov/973938">http://dic.academic.ru/dic.nsf/ushakov/973938</a>
 2. <a href="https://ru.wikipedia.org/wiki/Сноска">https://ru.wikipedia.org/wiki/Сноска</a>'''),
    )
    for i,x in enumerate(txs):
	print
	print ' --- ',i,' --- '
	print 'I:',x[0]
	o=thumbify(x[0])
	print 'O:',o[0]
	if o[0]==x[1]:
	    print '*** PASSED ***'
	else:
	    print '*** FAILED ***'
	    print 'E:',x[1]
	    raise AssertionError
