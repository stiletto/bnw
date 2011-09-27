# coding: utf-8

import unittest

class TestImport(unittest.TestCase):
    def test_core(self):
        import bnw_core.base
        import bnw_core.bnw_objects
        import bnw_core.ensure_indexes
        import bnw_core.post

    def test_global(self):
        import bnw_xmpp.bnw_component

    def test_xmpp(self):
        import bnw_xmpp.base
        import bnw_xmpp.handlers
        import bnw_xmpp.iq_handlers

    def test_web(self):
        import bnw_web.site
