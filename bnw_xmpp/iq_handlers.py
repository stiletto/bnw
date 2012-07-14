import base64
import StringIO

from twisted.words.xish import domish
from twisted.internet import defer
from twisted.internet.threads import deferToThread
from txmongo import gridfs
import Image

from base import send_raw
import bnw_core.base
import bnw_core.bnw_mongo
from bnw_core import bnw_objects as objs


def get_and_resize_avatar(iq):
    mimetype = str(iq.vCard.PHOTO.TYPE)
    if mimetype not in ('image/png', 'image/jpeg', 'image/gif'):
        return
    filedata = iq.vCard.PHOTO.BINVAL
    if not filedata:
        return
    filedata = str(filedata)
    if len(filedata) > 32768:
        # XEP-0153 says what image SHOULD be 8KB max,
        # let's approve up to 32KB.
        return
    try:
        avatar = base64.b64decode(filedata)
    except TypeError:
        return
    try:
        im = Image.open(StringIO.StringIO(avatar))
        im.thumbnail((48, 48), Image.ANTIALIAS)
        thumb_f = StringIO.StringIO()
        im.save(thumb_f, 'png')
    except IOError:
        return
    return avatar, mimetype, thumb_f.getvalue()

@defer.inlineCallbacks
def vcard(iq, iq_user):
    if not iq.vCard:
        defer.returnValue(False)
    if not iq_user:
        # User which have been sent IQ not registered.
        defer.returnValue(True)
    v = iq.vCard
    # Update avatar info.
    av_info = iq_user.get('avatar')
    if v.PHOTO:
        res = yield deferToThread(get_and_resize_avatar, iq)
        if res:
            avatar, mimetype, thumb = res
            fs = yield bnw_core.bnw_mongo.get_fs('avatars')
            update_needed = True
            if av_info:
                # TODO: Fix fs.get/GridOut.__init__ in txmongo
                doc = yield fs._GridFS__files.find_one({'_id': av_info[0]})
                f = yield fs.get(doc)
                old_avatar = yield f.read()
                if old_avatar == avatar:
                    update_needed = False
                else:
                    fs.delete(av_info[0])
                    fs.delete(av_info[2])
            if update_needed:
                extension = mimetype.split('/')[1]
                avid = fs.put(
                    avatar, filename=iq_user['name']+'.'+extension,
                    contentType=mimetype)
                thumbid = fs.put(
                    thumb, filename=iq_user['name']+'_thumb.png',
                    contentType='image/png')
                yield objs.User.mupdate(
                    {'name': iq_user['name']},
                    {'$set': {'avatar': [avid, mimetype, thumbid]}})
    elif av_info:
        fs = yield bnw_core.bnw_mongo.get_fs('avatars')
        fs.delete(av_info[0])
        fs.delete(av_info[2])
        yield objs.User.mupdate(
            {'name': iq_user['name']},
            {'$unset': {'avatar': 1}})
    # Update additional fields.
    vcard = {}
    if v.N and v.N.GIVEN and str(v.N.GIVEN) and v.N.FAMILY and str(v.N.FAMILY):
        vcard['fullname'] = '%s %s' % (v.N.GIVEN, v.N.FAMILY)
    if v.URL and str(v.URL): vcard['url'] = str(v.URL)
    if v.DESC and str(v.DESC): vcard['desc'] = str(v.DESC)
    yield objs.User.mupdate(
        {'name': iq_user['name']},
        {'$set': {'vcard': vcard}})
    defer.returnValue(True)

VERSION_XMLNS = 'jabber:iq:version'
def version(iq, iq_user):
    if iq.query and iq.query.uri == VERSION_XMLNS:
        reply = domish.Element((None,'iq'))
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
        reply = domish.Element((None,'iq'))
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
        reply = domish.Element((None,'iq'))
        reply['type'] = 'result'
        if iq.getAttribute('id'):
            reply['id'] = iq['id']
        reply.addElement('query', DISCO_INFO_XMLNS)
        reply.query.addElement('identity')
        reply.query.identity['category'] = 'client' # not pretty sure
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
