import base64
from cStringIO import StringIO

from twisted.words.xish import domish
from twisted.internet import defer, reactor
from twisted.internet.threads import deferToThread
from twisted.web.client import Agent
from twisted.web.http_headers import Headers
from twisted.web.iweb import IBodyProducer
from zope.interface import implements
from tornado.escape import utf8

#from txmongo import gridfs
import Image

from base import send_raw
import bnw.core.base
import bnw.core.bnw_mongo
from bnw.core import bnw_objects as objs
from bnw.core.base import config

class StringProducer(object):
    implements(IBodyProducer)

    def __init__(self, body):
        self.body = body
        self.length = len(body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return defer.succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass

agent = Agent(reactor)

def get_and_resize_avatar(iq):
    mimetype = str(iq.vCard.PHOTO.TYPE)
    if mimetype not in ('image/png', 'image/jpeg', 'image/gif'):
        return
    filedata = iq.vCard.PHOTO.BINVAL
    if not filedata:
        return
    filedata = str(filedata)
    if len(filedata) > 102400:
        # XEP-0153 says what image SHOULD be 8KB max,
        # let's approve up to 100KB.
        return
    try:
        missing_padding = 4 - len(filedata) % 4
        if missing_padding:
            filedata += '=' * missing_padding
        avatar = base64.b64decode(filedata)
    except TypeError:
        return
    try:
        im = Image.open(StringIO(avatar))
        if im.size[0]*im.size[1] > 1024**2:
            # we won't generate thumbnails for avatars larger than 1024x1024
            # because uhm...well... fuck you
            print 'Avatar from %s is too large.' % (iq['from'],), im.size
            return
        im.thumbnail((48, 48), Image.ANTIALIAS)
        thumb_f = StringIO()
        im.save(thumb_f, 'png')
    except IOError:
        return
    return avatar, mimetype, thumb_f.getvalue()


@defer.inlineCallbacks
def vcard(iq, iq_user):
    if (not iq.vCard) or iq['type'] != 'result':
        defer.returnValue(False)
    if not iq_user:
        # User which have been sent IQ not registered.
        defer.returnValue(True)
    v = iq.vCard
    # Update avatar info.
    av_info = iq_user.get('avatar')
    av_key = 'avatars/' + iq_user['name']
    if v.PHOTO and config.blob_storage:
        res = yield deferToThread(get_and_resize_avatar, iq)
        if res:
            avatar, mimetype, thumb = res
            yield agent.request('PUT',utf8(config.blob_storage+'put/'+av_key),
                Headers({'Content-Type': [mimetype],
                         'Content-Length': [str(len(avatar))]}), StringProducer(avatar))
            yield agent.request('PUT',utf8(config.blob_storage+'put/'+av_key+'/thumb'),
                Headers({'Content-Type': ['image/png'],
                         'Content-Length': [str(len(thumb))]}), StringProducer(thumb))
            yield objs.User.mupdate(
                {'name': iq_user['name']},
                    {'$set': {'avatar': 'blobstorage'}})
    elif av_info and config.blob_storage:
        yield agent.request('DELETE',utf8(config.blob_storage+'delete/'+av_key))
        yield agent.request('DELETE',utf8(config.blob_storage+'delete/'+av_key+'/thumb'))
        yield objs.User.mupdate(
            {'name': iq_user['name']},
            {'$unset': {'avatar': 1}})
    # Update additional fields.
    vcard = {}
    if v.N and v.N.GIVEN and str(v.N.GIVEN) and v.N.FAMILY and str(v.N.FAMILY):
        vcard['fullname'] = '%s %s' % (v.N.GIVEN, v.N.FAMILY)
    if v.URL and str(v.URL):
        vcard['url'] = str(v.URL)
    if v.DESC and str(v.DESC):
        vcard['desc'] = str(v.DESC)
    yield objs.User.mupdate(
        {'name': iq_user['name']},
        {'$set': {'vcard': vcard}})
    defer.returnValue(True)

VERSION_XMLNS = 'jabber:iq:version'


def version(iq, iq_user):
    if iq.query and iq.query.uri == VERSION_XMLNS:
        reply = domish.Element((None, 'iq'))
        reply['type'] = 'result'
        if iq.getAttribute('id'):
            reply['id'] = iq['id']
        reply.addElement('query', VERSION_XMLNS)
        reply.query.addElement('name', content='BnW')
        reply.query.addElement('version', content='0.1')
        reply.query.addElement('os', content='OS/360')
        send_raw(iq['from'], iq['to'], reply)
        return True

DISCO_ITEMS_XMLNS = 'http://jabber.org/protocol/disco#items'


def disco_items(iq, iq_user):
    if iq.query and iq.query.uri == DISCO_ITEMS_XMLNS:
        reply = domish.Element((None, 'iq'))
        reply['type'] = 'result'
        if iq.getAttribute('id'):
            reply['id'] = iq['id']
        reply.addElement('query', DISCO_ITEMS_XMLNS)
        send_raw(iq['from'], iq['to'], reply)
        return True

DISCO_INFO_XMLNS = 'http://jabber.org/protocol/disco#info'
FEATURES = ('jabber:iq:version',
            'http://jabber.org/protocol/chatstates',
            'http://jabber.org/protocol/disco#info',
            'http://jabber.org/protocol/disco#items',
            'urn:xmpp:receipts',
            )


def disco_info(iq, iq_user):
    if iq.query and iq.query.uri == DISCO_INFO_XMLNS:
        reply = domish.Element((None, 'iq'))
        reply['type'] = 'result'
        if iq.getAttribute('id'):
            reply['id'] = iq['id']
        reply.addElement('query', DISCO_INFO_XMLNS)
        reply.query.addElement('identity')
        reply.query.identity['category'] = 'client'  # not pretty sure
        reply.query.identity['type'] = 'bot'
        reply.query.identity['name'] = 'BnW'

        for feature_name in FEATURES:
            feature = reply.query.addElement('feature')
            feature['var'] = feature_name

        send_raw(iq['from'], iq['to'], reply)
        return True

handlers = [
    vcard,
    version,
    disco_items,
    disco_info,
]
