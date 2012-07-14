from twisted.words.xish import domish

from base import require_auth
from bnw_xmpp.base import send_raw


@require_auth
def cmd_vcard(request, safe=None):
    """Request user's vCard."""
    reply = domish.Element((None, 'iq'))
    reply.addUniqueId()
    reply['type'] = 'get'
    reply.addElement('vCard', 'vcard-temp')
    send_raw(request.user['jid'], None, reply)
    return dict(ok=True, desc='vCard has been requested.')
