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
    """Get base url for links in accordance with baseurl user setting.
    baseurl can be one of:
        "http": return http base url
        "https": return https base url
        "random string": return this string
        None: return http base url
    """
    if 'baseurl' in user['settings']:
        baseurl = user['settings']['baseurl']
        if baseurl == 'http':
            return get_http_webui_base()
        elif baseurl == 'https':
            return get_https_webui_base()
        else:
            return baseurl
    else:
        return get_http_webui_base()

def get_https_webui_base():
    return "https://" + config.webui_base

def get_http_webui_base():
    return "http://" + config.webui_base
