import time
import traceback

#from twisted.python import log
#from twisted.web.xmlrpc import Proxy

from bnw.core.base import config
from bnw.handlers.base import require_auth, check_arg


@check_arg(page='[0-9]+')
def cmd_search(request, query='', page='0'):
    return dict(ok=False, desc='Sorry, search is temporary broken.')
    if not query:
        return dict(ok=False, desc='So where is your query?')
    if len(query) > 2048:
        return dict(ok=False, desc='Search query is too long.')

    service = Proxy('http://127.0.0.1:%d/' % config.search_port)
    start = time.time()
    try:
        result = service.callRemote('search', query, int(page))
    except Exception:
        log.msg('SEARCH ERROR:\n\n' + traceback.format_exc())
        return dict(ok=False, desc='Search internal error.')
    else:
        if result is None:
            return dict(ok=False, desc='Bad request.')

    t = time.time() - start
    log.msg('Queried "%s" by %s. Found %s results in %.3fs.' % (
        query, request.user['name'] if request.user else '*', result['estimated'], t))
    return dict(ok=True, format='search', **result)
