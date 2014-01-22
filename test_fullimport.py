# coding: utf-8

import unittest

class TestImport(unittest.TestCase):
    def test_core(self):
        import bnw.core.base
        import bnw.core.bnw_objects
        import bnw.core.ensure_indexes
        import bnw.core.post

    def test_global(self):
        import bnw.xmpp.bnw_component

    def test_xmpp(self):
        import bnw.xmpp.base
        import bnw.xmpp.handlers
        import bnw.xmpp.iq_handlers

    def test_web(self):
        import bnw.web.site
