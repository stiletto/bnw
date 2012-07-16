#
# Copyright 2012 Stiletto <blasux@blasux.ru>
#
# Licensed under the MIT License.
#
# coding: utf-8
from bnw_web.linkshit import linkparse

import unittest

class LinkShitTest(unittest.TestCase):
    def test_linkshit(self):
        a = linkparse(u'Ololo lololo #67AB3D fyuck http://bnw.im/u/lol http://ompldr.org/vZGZ1aw damn #ABCDEF/XYZ shit-@govnoeb')
        assert a.next() == 'Ololo lololo '
        assert a.next() == ('msg','#67AB3D','67AB3D')
        assert a.next() == ' fyuck '
        assert a.next() == ('url','http://bnw.im/u/lol','http://bnw.im/u/lol')
        assert a.next() == ' '
        assert a.next() == ('url','http://ompldr.org/vZGZ1aw','http://ompldr.org/vZGZ1aw')
        assert a.next() == ' damn '
        assert a.next() == ('msg','#ABCDEF/XYZ','ABCDEF/XYZ')
        assert a.next() == ' shit-'
        assert a.next() == ('user','@govnoeb','govnoeb')
        pass


if __name__=="__main__":
    unittest.main()
