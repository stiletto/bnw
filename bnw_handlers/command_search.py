import time
import traceback
from twisted.python import log
from twisted.internet import defer
from twisted.web.xmlrpc import Proxy
from bnw_handlers.base import require_auth


@require_auth
@defer.inlineCallbacks
def cmd_search(request, text):
    if len(text) > 2048:
        defer.returnValue(dict(ok=False, desc='Search query is too long.'))
    service = Proxy('http://127.0.0.1:7850/')
    start = time.time()
    try:
        result = yield service.callRemote('search', text)
    except Exception:
        log.msg('SEARCH ERROR:\n\n' + traceback.format_exc())
        defer.returnValue(dict(ok=False, desc='Sorry, search not available.'))

    t = time.time() - start
    log.msg('Queried "%s" by %s. Found %s results in %.3fs.' % (
        text, request.user['name'], result[0], t))
    defer.returnValue(dict(ok=True, format='search', search_result=result))
