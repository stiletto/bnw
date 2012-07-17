# coding: utf-8
#
# Copyright 2012 Stiletto <blasux@blasux.ru>
#
# Licensed under the MIT License.
#

from twisted.trial import unittest
from bnw_web.linkshit import linkparse


class LinkShitTest(unittest.TestCase):
    def test_simple(self):
        a = linkparse(u'Ololo lololo #67AB3D fyuck http://bnw.im/u/lol http://ompldr.org/vZGZ1aw damn #ABCDEF/XYZ shit-@govnoeb @user_with_undescores')

        self.assertEqual(a.next(), 'Ololo lololo ')
        self.assertEqual(a.next(), ('msg', '#67AB3D', '67AB3D'))
        self.assertEqual(a.next(), ' fyuck ')
        self.assertEqual(a.next(), (
            'url','http://bnw.im/u/lol',
            'http://bnw.im/u/lol', 'http://bnw.im/u/lol'))
        self.assertEqual(a.next(), ' ')
        self.assertEqual(a.next(), (
            'url', 'http://ompldr.org/vZGZ1aw',
            'http://ompldr.org/vZGZ1aw', 'http://ompldr.org/vZGZ1aw'))
        self.assertEqual(a.next(), ' damn ')
        self.assertEqual(a.next(), ('msg', '#ABCDEF/XYZ', 'ABCDEF/XYZ'))
        self.assertEqual(a.next(), ' shit-')
        self.assertEqual(a.next(), ('user', '@govnoeb', 'govnoeb'))
        self.assertEqual(a.next(), ' ')
        self.assertEqual(a.next(), (
            'user', '@user_with_undescores', 'user_with_undescores'))

    def test_clip_long_url(self):
        a = linkparse(u'http://ru.wikipedia.org/wiki/Гиперинфляция#.D0.A0.D0.B5.D0.BA.D0.BE.D1.80.D0.B4.D0.BD.D1.8B.D0.B5_.D0.BF.D1.80.D0.B8.D0.BC.D0.B5.D1.80.D1.8B_.D0.B3.D0.B8.D0.BF.D0.B5.D1.80.D0.B8.D0.BD.D1.84.D0.BB.D1.8F.D1.86.D0.B8.D0.B8')

        self.assertEqual(a.next(), '')
        self.assertEqual(a.next(), (
            'url',
            u'http://ru.wikipedia.org/wiki/Гиперинфляция#.D0.A0.D0.B5.D0.BA.D0.BE.D1.80.D0.B4.D0.BD.D1.8B.D0.B5_.D0.BF.D1.80.D0.B8.D0.BC.D0.B5.D1.80.D1.8B_.D0.B3.D0.B8.D0.BF.D0.B5.D1.80.D0.B8.D0.BD.D1.84.D0.BB.D1.8F.D1.86.D0.B8.D0.B8',
            u'http://ru.wikipedia.org/wiki/Гиперинфляция#.D0.A0.D0.B5.D0.BA.D0.BE.D1.80.D0.B4.D0.BD.D1.8B.D0.B5_.D0.BF.D1.80.D0.B8.D0.BC.D0.B5.D1.80.D1.8B_.D0.B3.D0.B8.D0.BF.D0.B5.D1.80.D0.B8.D0.BD.D1.84.D0.BB.D1.8F.D1.86.D0.B8.D0.B8',
            u'http://ru.wikipedia.org/wiki/Гиперинфляц.....0.B8.D0.B8'))
