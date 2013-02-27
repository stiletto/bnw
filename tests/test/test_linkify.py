# coding: utf-8

from twisted.trial import unittest

from bnw_web.linkify import linkify


def l(text):
    return linkify(text, format="moinmoin")


class LinkifyTest(unittest.TestCase):

    def test_simple_formatting(self):
        self.assertEqual(
            l('test //test test// test **test test** test'),
            'test <i>test test</i> test <b>test test</b> test')

    def test_nested_formatting(self):
        self.assertEqual(
            l(u'Test *жирный* **жирный** ***жирный*** //курсив **жирный курсив**//'),
            u'Test *жирный* <b>жирный</b> <b>*жирный</b>* <i>курсив <b>жирный курсив</b></i>')

    def test_broken_formatting(self):
        self.assertEqual(
            l('test //test **test// test** test'),
            'test <i>test <b>test</b></i><b> test</b> test')
        self.assertEqual(
            l('**test'),
            '<b>test</b>')

    def test_named_links(self):
        self.assertEqual(
            l(u'''Обычный Советский Дурдом: http://allin777.livejournal.com/152675.html
[[ http://allin777.livejournal.com/152675.html|Обычный Советский Дурдом]]
"ИЗ РЕЧИ НИКОЛАЯ ЕЖОВА НА ПЛЕНУМЕ ЦК ВКП(б)
1 марта 1937 г.
ЕЖОВ. #ABCDEF Здесь заодно, товарищи разрешите сказать о таких умонастроениях, таких некоторых хозяйственников'''),
            u'''Обычный Советский Дурдом: <a href="http://allin777.livejournal.com/152675.html">http://allin777.livejournal.com/152675.html</a>
<a href="http://allin777.livejournal.com/152675.html">Обычный Советский Дурдом</a>
&quot;ИЗ РЕЧИ НИКОЛАЯ ЕЖОВА НА ПЛЕНУМЕ ЦК ВКП(б)
1 марта 1937 г.
ЕЖОВ. <a href="/p/ABCDEF">#ABCDEF</a> Здесь заодно, товарищи разрешите сказать о таких умонастроениях, таких некоторых хозяйственников''')

        self.assertEqual(
            l(u'''Wiki-разметка для ссылок (я про [[URL | text]] сейчас), как по мне, выглядит убого. Может, конвертировать её в что-то типа примечаний[1] или сносок[2]?
     1. http://dic.academic.ru/dic.nsf/ushakov/973938
     2. https://ru.wikipedia.org/wiki/Сноска'''),
            u'''Wiki-разметка для ссылок (я про <a href="http://URL">text</a> сейчас), как по мне, выглядит убого. Может, конвертировать её в что-то типа примечаний[1] или сносок[2]?
     1. <a href="http://dic.academic.ru/dic.nsf/ushakov/973938">http://dic.academic.ru/dic.nsf/ushakov/973938</a>
     2. <a href="https://ru.wikipedia.org/wiki/Сноска">https://ru.wikipedia.org/wiki/Сноска</a>''')

        self.assertEqual(
            l(u'[[http://няшные котики]]]'),
            u'[[<a href="http://няшные">http://няшные</a> котики]]]')
