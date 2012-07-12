import random
from twisted.internet import defer

from delayed_global import DelayedGlobal

idchars='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    
def genid(idlen):
    return ''.join(random.choice(idchars) for i in xrange(0,idlen))
    
def cropstring(string,maxlen):
    return string if len(string)<=maxlen else string[:maxlen]+u'...'
        
def _(s,user):
    return s
    
notifiers = set()
#connection_class = DelayedGlobal('connection_class')

class BnwResponse(Exception): # we do it idiotic way!
    pass

config = DelayedGlobal('config')

def get_webui_base(user):
    """Get http or https base address for links in accordance with
    httpslinks user setting.
    """
    if ('httpslinks' in user['settings'] and
        user['settings']['httpslinks'] == 'on'):
            return get_https_webui_base()
    else:
            return get_http_webui_base()

def get_https_webui_base():
    return "https://" + config.webui_base

def get_http_webui_base():
    return "http://" + config.webui_base
