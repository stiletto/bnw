# -*- coding: utf-8 -*-

import os
import random
import time
from widgets import widgets
import PyRSS2Gen
from datetime import datetime
from bnw.formatting import linkify

from xml.sax import saxutils

try:
    XMLGenerator = saxutils.LexicalXMLGenerator
except:
    XMLGenerator = saxutils.XMLGenerator


class BnwRSSFeed(PyRSS2Gen.RSS2):
    rss_attrs = {
        "version": "2.0",
        "xmlns:atom": "http://www.w3.org/2005/Atom",
        "xmlns:slash": "http://purl.org/rss/1.0/modules/slash/",
        "xmlns:rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "xmlns:image": "http://purl.org/rss/1.0/modules/image/",
    }

    def write_xml(self, outfile, encoding="iso-8859-1"):
        handler = XMLGenerator(outfile, encoding)
        handler.startDocument()
        self.publish(handler)
        handler.endDocument()

    def publish_extensions(self, handler):
        if self.selflink:
            PyRSS2Gen._element(handler, 'atom:link', None,
                               {'rel': 'self',
                                'type': 'application/rss+xml',
                                'href': self.selflink,
                                })


class BnwDescription(object):
    def __init__(self, text):
        self.text = text or ''

    def publish(self, handler):
        handler.startElement('description', {})
        # handler.startCDATA()
        handler._write(u'<![CDATA[')
        # handler.characters(self.text)
        handler._write(self.text.replace(']]>', ']]&gt;'))
        handler._write(u']]>')
        # handler.endCDATA()
        handler.endElement('description')


class AtomSelf(object):
    def __init__(self, link):
        self.link = link

    def publish(self, handler):
        handler.startElement('atom:link',
                             {'rel': 'self',
                              'type': 'application/rss+xml',
                              'href': self.link,
                              })
        handler.endElement('atom:link')


def message_feed(messages, link, title, *args, **kwargs):
    rss_items = [PyRSS2Gen.RSSItem(  # author=msg['user'],
        link=widgets.post_url(msg['id']),
        guid=widgets.post_url(msg['id']),
        pubDate=datetime.utcfromtimestamp(msg['date']),
        categories=set(msg['tags']) | set(msg['clubs']),
        title='@%s: #%s' % (msg['user'], msg['id']),
        description=BnwDescription(linkify(msg['text'], msg.get('format')).replace('\n', '<br/>'))) for msg in messages]

    rss_feed = BnwRSSFeed(title=title,
                          link=link,
                          description=None,
                          docs=None,
                          items=rss_items,
                          *args, **kwargs)
    rss_feed.selflink = link + '/?format=rss'
    return rss_feed.to_xml(encoding='utf-8')
