# -*- coding: utf-8 -*-
import re
import unittest

from bnw.xmpp.handlers import simple_handlers




(POST_REGEX, _) = simple_handlers[-1]

#REGEX = ur'(?:((?P<anonymous>ANON|ФТЩТ)\s+)?(?P<tag1>[\*!]\S+)?(?:\s+(?P<tag2>[\*!]\S+))?(?:\s+(?P<tag3>[\*!]\S+))?(?:\s+(?P<tag4>[\*!]\S+))?(?:\s+(?P<tag5>[\*!]\S+))?\s+)?(?P<text>.+)'


class TestPostSimplifiedRegex(unittest.TestCase):
    def setUp(self):
        self.regex = re.compile(POST_REGEX)

    def test_only_text(self):
        def check_regex(result, text):
            self.assertIsNotNone(result, text)
            groups = result.groupdict()
            self.assertIsNotNone(groups.get('text'), text)
        text = "this is long post"
        check_regex(self.regex.match(text), text)

    def test_1tag_text(self):
        def check_regex(result, text):
            self.assertIsNotNone(result, text)
            groups = result.groupdict()
            self.assertIsNotNone(groups.get('text'), text)
            self.assertIsNotNone(groups.get('tag1'), text)
        texts = ["*tag1 this is long post",
                "*tag1    this is long post",
                "*tag1      this is long post"]
        for text in texts:
            check_regex(self.regex.match(text), text)

    def test_2tag_text(self):
        def check_regex(result, text):
            self.assertIsNotNone(result)
            groups = result.groupdict()
            self.assertIsNotNone(groups.get('text'), text)
            self.assertIsNotNone(groups.get('tag1'), text)
            self.assertIsNotNone(groups.get('tag2'), text)
        texts = ["*tag1 *tag2 this is long post",
                 "*tag1 *tag2    this is long post",
                 "*tag1   *tag2 this is long post",
                 "*tag1     *tag2 this is long post",
                 "*tag1     *tag2    this is long post"]
        for text in texts:
            check_regex(self.regex.match(text), text)

    def test_3tag_text(self):
        def check_regex(result, text):
            self.assertIsNotNone(result)
            groups = result.groupdict()
            self.assertIsNotNone(groups.get('text'), text)
            self.assertIsNotNone(groups.get('tag1'), text)
            self.assertIsNotNone(groups.get('tag2'), text)
            self.assertIsNotNone(groups.get('tag3'), text)

        texts = ["*tag1 *tag2 *tag3 this is long post",
                 "*tag1 *tag2 *tag3  this is long post",
                 "*tag1  *tag2 *tag3  this is long post",
                 "*tag1    *tag2 *tag3  this is long post",
                 "*tag1 *tag2  *tag3  this is long post",
                 "*tag1 *tag2   *tag3  this is long post",
                 "*tag1    *tag2   *tag3  this is long post"]
        for text in texts:
            check_regex(self.regex.match(text), text)

    def test_4tag_text(self):
        def check_regex(result, text):
            self.assertIsNotNone(result, text)
            groups = result.groupdict()
            self.assertIsNotNone(groups.get('text'), text)
            self.assertIsNotNone(groups.get('tag1'), text)
            self.assertIsNotNone(groups.get('tag2'), text)
            self.assertIsNotNone(groups.get('tag3'), text)
            self.assertIsNotNone(groups.get('tag4'), text)
        texts = ["*tag1 *tag2 *tag3 *tag4 this is long post",
                 "*tag1 *tag2 *tag3  *tag4 this is long post",
                 "*tag1  *tag2 *tag3  *tag4 this is long post",
                 "*tag1    *tag2 *tag3  *tag4 this is long post",
                 "*tag1 *tag2  *tag3  *tag4 this is long post",
                 "*tag1 *tag2   *tag3  *tag4 this is long post",
                 "*tag1    *tag2   *tag3  *tag4 this is long post"]
        for text in texts:
            check_regex(self.regex.match(text), text)

    def test_5tag_text(self):
        def check_regex(result, text):
            self.assertIsNotNone(result, text)
            groups = result.groupdict()
            self.assertIsNotNone(groups.get('text'), text)
            self.assertIsNotNone(groups.get('tag1'), text)
            self.assertIsNotNone(groups.get('tag2'), text)
            self.assertIsNotNone(groups.get('tag3'), text)
            self.assertIsNotNone(groups.get('tag4'), text)
            self.assertIsNotNone(groups.get('tag5'), text)
        texts = ["*tag1 *tag2 *tag3 *tag4 *tag5 this is long post",
                 "*tag1 *tag2 *tag3  *tag4  *tag5  this is long post",
                 "*tag1  *tag2 *tag3  *tag4  *tag5  this is long post",
                 "*tag1    *tag2 *tag3  *tag4  *tag5  this  is long post",
                 "*tag1 *tag2  *tag3  *tag4   *tag5  this is long post",
                 "*tag1 *tag2   *tag3  *tag4  *tag5  this is long post",
                 "*tag1    *tag2   *tag3  *tag4   *tag5  this is long post"]
        for text in texts:
            check_regex(self.regex.match(text), text)


class TestAnonPostSimplifiedRegex(unittest.TestCase):
    def setUp(self):
        self.regex = re.compile(POST_REGEX)

    def test_only_text_anon(self):
        text = "this is long post"
        self.assertIsNotNone(self.regex.match(text), text)

    def test_1tag_text_anon(self):
        def check_regex(result, text):
            self.assertIsNotNone(result, text)
            groups = result.groupdict()
            self.assertIsNotNone(groups.get('anonymous'), text)
            self.assertIsNotNone(groups.get('text'), text)
            self.assertIsNotNone(groups.get('tag1'), text)
        texts = [u"ANON *tag1 this is long post",
                u"ANON   *tag1    this is long post",
                u"ANON *tag1      this is long post",
                u"ФТЩТ *tag1 this is long post",
                u"ФТЩТ   *tag1    this is long post",
                u"ФТЩТ *tag1      this is long post"]
        for text in texts:
            check_regex(self.regex.match(text), text)

    def test_2tag_text_anon(self):
        def check_regex(result, text):
            self.assertIsNotNone(result, text)
            groups = result.groupdict()
            self.assertIsNotNone(groups.get('anonymous'), text)
            self.assertIsNotNone(groups.get('text'), text)
            self.assertIsNotNone(groups.get('tag1'), text)
            self.assertIsNotNone(groups.get('tag2'), text)
        texts = [u"ANON   *tag1 *tag2 this is long post",
                 u"ANON  *tag1 *tag2    this is long post",
                 u"ANON  *tag1   *tag2 this is long post",
                 u"ANON   *tag1     *tag2 this is long post",
                 u"ANON   *tag1     *tag2    this is long post",

                 u"ФТЩТ  *tag1 *tag2 this is long post",
                 u"ФТЩТ   *tag1 *tag2    this is long post",
                 u"ФТЩТ  *tag1   *tag2 this is long post",
                 u"ФТЩТ   *tag1     *tag2 this is long post",
                 u"ФТЩТ   *tag1     *tag2    this is long post"]
        for text in texts:
            check_regex(self.regex.match(text), text)

    def test_3tag_text_anon(self):
        def check_regex(result, text):
            self.assertIsNotNone(result, text)
            groups = result.groupdict()
            self.assertIsNotNone(groups.get('anonymous'), text)
            self.assertIsNotNone(groups.get('text'), text)
            self.assertIsNotNone(groups.get('tag1'), text)
            self.assertIsNotNone(groups.get('tag2'), text)
            self.assertIsNotNone(groups.get('tag3'), text)

        texts = [u"ANON   *tag1 *tag2 *tag3 this is long post",
                 u"ANON   *tag1 *tag2 *tag3  this is long post",
                 u"ANON   *tag1  *tag2 *tag3  this is long post",
                 u"ANON   *tag1    *tag2 *tag3  this is long post",
                 u"ANON   *tag1 *tag2  *tag3  this is long post",
                 u"ANON   *tag1 *tag2   *tag3  this is long post",
                 u"ANON   *tag1    *tag2   *tag3  this is long post",


                 u"ФТЩТ   *tag1 *tag2 *tag3 this is long post",
                 u"ФТЩТ   *tag1 *tag2 *tag3  this is long post",
                 u"ФТЩТ   *tag1  *tag2 *tag3  this is long post",
                 u"ФТЩТ   *tag1    *tag2 *tag3  this is long post",
                 u"ФТЩТ   *tag1 *tag2  *tag3  this is long post",
                 u"ФТЩТ   *tag1 *tag2   *tag3  this is long post",
                 u"ФТЩТ   *tag1    *tag2   *tag3  this is long post",
                 ]
        for text in texts:
            check_regex(self.regex.match(text), text)

    def test_4tag_text_anon(self):
        def check_regex(result, text):
            self.assertIsNotNone(result, text)
            groups = result.groupdict()
            self.assertIsNotNone(groups.get('anonymous'), text)
            self.assertIsNotNone(groups.get('text'), text)
            self.assertIsNotNone(groups.get('tag1'), text)
            self.assertIsNotNone(groups.get('tag2'), text)
            self.assertIsNotNone(groups.get('tag3'), text)
            self.assertIsNotNone(groups.get('tag4'), text)
        texts = [u"ANON   *tag1 *tag2 *tag3 *tag4 this is long post",
                 u"ANON   *tag1 *tag2 *tag3  *tag4 this is long post",
                 u"ANON   *tag1  *tag2 *tag3  *tag4 this is long post",
                 u"ANON   *tag1    *tag2 *tag3  *tag4 this is long post",
                 u"ANON   *tag1 *tag2  *tag3  *tag4 this is long post",
                 u"ANON   *tag1 *tag2   *tag3  *tag4 this is long post",
                 u"ANON   *tag1    *tag2   *tag3  *tag4 this is long post",

                 u"ФТЩТ   *tag1 *tag2 *tag3 *tag4 this is long post",
                 u"ФТЩТ   *tag1 *tag2 *tag3  *tag4 this is long post",
                 u"ФТЩТ   *tag1  *tag2 *tag3  *tag4 this is long post",
                 u"ФТЩТ   *tag1    *tag2 *tag3  *tag4 this is long post",
                 u"ФТЩТ   *tag1 *tag2  *tag3  *tag4 this is long post",
                 u"ФТЩТ   *tag1 *tag2   *tag3  *tag4 this is long post",
                 u"ФТЩТ   *tag1    *tag2   *tag3  *tag4 this is long post",
                 ]
        for text in texts:
            check_regex(self.regex.match(text), text)

    def test_5tag_text_anon(self):
        def check_regex(result, text):
            self.assertIsNotNone(result, text)
            groups = result.groupdict()
            self.assertIsNotNone(groups.get('anonymous'), text)
            self.assertIsNotNone(groups.get('text'), text)
            self.assertIsNotNone(groups.get('tag1'), text)
            self.assertIsNotNone(groups.get('tag2'), text)
            self.assertIsNotNone(groups.get('tag3'), text)
            self.assertIsNotNone(groups.get('tag4'), text)
            self.assertIsNotNone(groups.get('tag5'), text)
        texts = [u"ANON   *tag1 *tag2 *tag3 *tag4 *tag5 this is long post",
                 u"ANON   *tag1 *tag2 *tag3  *tag4  *tag5  this is long post",
                 u"ANON   *tag1  *tag2 *tag3  *tag4  *tag5  this is long post",
                 u"ANON   *tag1    *tag2 *tag3  *tag4  *tag5  this  is long post",
                 u"ANON   *tag1 *tag2  *tag3  *tag4   *tag5  this is long post",
                 u"ANON   *tag1 *tag2   *tag3  *tag4  *tag5  this is long post",
                 u"ANON   *tag1    *tag2   *tag3  *tag4   *tag5  this is long post",


                 u"ФТЩТ   *tag1 *tag2 *tag3 *tag4 *tag5 this is long post",
                 u"ФТЩТ   *tag1 *tag2 *tag3  *tag4  *tag5  this is long post",
                 u"ФТЩТ   *tag1  *tag2 *tag3  *tag4  *tag5  this is long post",
                 u"ФТЩТ   *tag1    *tag2 *tag3  *tag4  *tag5  this  is long post",
                 u"ФТЩТ   *tag1 *tag2  *tag3  *tag4   *tag5  this is long post",
                 u"ФТЩТ   *tag1 *tag2   *tag3  *tag4  *tag5  this is long post",
                 u"ФТЩТ   *tag1    *tag2   *tag3  *tag4   *tag5  this is long post"]
        for text in texts:
            check_regex(self.regex.match(text), text)


if __name__ == '__main__':
    unittest.main()
