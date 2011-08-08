# -*- coding: utf-8 -*-
import re
from widgets import widgets

from tornado.escape import _unicode,xhtml_escape,url_escape
#def _unicode(value):
#    if isinstance(value, str):
#        return value.decode("utf-8")
#    assert isinstance(value, unicode)
#    return value

linkhostings = [
    (ur'http://rghost.ru/([0-9]+)', lambda h,p,u,m,n: (
        u'<a class="imglink" href="%s"%s>[%d]</a>'% (h,p,n),
        u'<a class="imglink" href="%s.view"%s><img class="imgpreview imgpreview_ps" src="http://rghost.ru/%s/thumb.png"/></a>'% (h,p,m.group(1)))),
    (ur'http://imgur.com/([A-Za-z0-9]+)', lambda h,p,u,m,n: (
        u'<a class="imglink" href="%s"%s>[%d]</a>'% (h,p,n),
        u'<a class="imglink" href="%s"%s><img class="imgpreview imgpreview_ps" src="http://i.imgur.com/%ss.png"/></a>'% (h,p,m.group(1)))),
    (ur'(http://ompldr.org/v([A-Za-z0-9]+))(/.+)?', lambda h,p,u,m,n: ( 
        u'<a class="imglink" href="%s"%s>[%d]</a>' % (m.group(1),p,n), 
        u'<a class="imglink" href="%s"%s><img class="imgpreview imgpreview_ps" src="http://ompldr.org/t%s"/></a>' % (m.group(1),p,m.group(2)) )),
    (ur'http://2-ch.ru/([a-z]+)/src/([0-9]+).(png|gif|jpg)', lambda h,p,u,m,n: (
        u'<a class="imglink" href="%s"%s>[%d]</a>' % (m.group(1),p,n),
        u'<a class="imglink" href="%s"%s><img class="imgpreview imgpreview_ps" src="http://2-ch.ru/%s/thumb/%ss.%s"/></a>' % (h,p,m.group(1),m.group(2),m.group(3)) )),
    (ur'http://(.+.(?:png|gif|jpg|jpeg))', lambda h,p,u,m,n: (
        u'<a class="imglink" href="%s"%s>[%d]</a>' % (h,p,n),
        u'<a class="imglink" href="%s"%s><img class="imgpreview imgpreview_ps imgpgen" src="http://fuck.blasux.ru/thumb?img=%s"/></a>' % (h,p,url_escape(h)) )),
]
linkhostings=[(re.compile('^'+k+'$'),v,k) for (k,v) in linkhostings]
#inkhosting=dict((re.compile(k),v) for (k,v) in linkhosting.iteritems())

_URL_RE = re.compile(ur"""\b((?:([\w-]+):(/{1,3})|www[.])(?:(?:(?:[^\s&()]|&amp;|&quot;)*(?:[^!"#$%&'()*+,.:;<=>?@\[\]^`{|}~\s]))|(?:\((?:[^\s&()]|&amp;|&quot;)*\)))+)""")
#_USER_RE = re.compile(ur"""(?:(?<=[\s\W])|^)@([0-9A-Za-z-]+)""")
_USER_RE = re.compile(ur"""(?:(?<=[\s\W])|^)@([0-9A-Za-z-]+)""")
_MSG_RE = re.compile(ur"""(?:(?<=[\s\W])|^)#([0-9A-Za-z]+)(?:/([0-9A-Za-z]+))?""")

_USER_LINK_RE = re.compile(ur"""http://bnw.im/u/([0-9A-Za-z-]+)""")
_MSG_LINK_RE = re.compile(ur"""http://bnw.im/p/([0-9A-Za-z-]+)(?:#([0-9A-Za-z]+))?""")

#_COMMENT_RE = re.compile(ur"""(?:(?<=[\s\W])|^)#([0-9A-Za-z]+/[0-9A-Za-z]+)""")
#_MSG_RE = re.compile(ur"""(?:(?<=[\s\W])|^)#([0-9A-Za-z]+)""")
#_MSG_RE = re.compile(ur"""(?:(?<=[\s\W])|^)#([0-9A-Za-z]+)""")

def linkify(text, shorten=True, extra_params="",
            require_protocol=False, permitted_protocols=["http", "https"]):
    """Converts plain text into HTML with links.

    For example: linkify("Hello http://tornadoweb.org!") would return
    Hello <a href="http://tornadoweb.org">http://tornadoweb.org</a>!

    Parameters:
    shorten: Long urls will be shortened for display.
    extra_params: Extra text to include in the link tag,
        e.g. linkify(text, extra_params='rel="nofollow" class="external"')
    require_protocol: Only linkify urls which include a protocol. If this is
        False, urls such as www.facebook.com will also be linkified.
    permitted_protocols: List (or set) of protocols which should be linkified,
        e.g. linkify(text, permitted_protocols=["http", "ftp", "mailto"]).
        It is very unsafe to include protocols such as "javascript".
    """
    if extra_params:
        extra_params = " " + extra_params.strip()

    appends=[]
    lnum={'n':0}
    
    def make_link(m):
        url = m.group(1)
        proto = m.group(2)
        if require_protocol and not proto:
            return url  # not protocol, no linkify

        if proto and proto not in permitted_protocols:
            return url  # bad protocol, no linkify

        href = m.group(1)
        if not proto:
            href = "http://" + href   # no proto specified, use http

        params = extra_params

        # clip long urls. max_len is just an approximation
        max_len = 30
        if shorten and len(url) > max_len:
            before_clip = url
            if proto:
                proto_len = len(proto) + 1 + len(m.group(3) or "")  # +1 for :
            else:
                proto_len = 0

            parts = url[proto_len:].split("/")
            if len(parts) > 1:
                # Grab the whole host part plus the first bit of the path
                # The path is usually not that interesting once shortened
                # (no more slug, etc), so it really just provides a little
                # extra indication of shortening.
                url = url[:proto_len] + parts[0] + "/" + \
                        parts[1][:8].split('?')[0].split('.')[0]

            if len(url) > max_len * 1.5:  # still too long
                url = url[:max_len]

            if url != before_clip:
                amp = url.rfind('&')
                # avoid splitting html char entities
                if amp > max_len - 5:
                    url = url[:amp]
                url += "..."

                if len(url) >= len(before_clip):
                    url = before_clip
                else:
                    # full url is visible on mouse-over (for those who don't
                    # have a status bar, such as Safari by default)
                    params += ' title="%s"' % href

        for (k,h,r) in linkhostings:
            m=k.match(href)
            if m:
                lnum['n']+=1 # ЕМ ГОВНО, ЕДУ КРЫШЕЙ, НЕ УМЕЮ ДУМАТЬ
                ret,app=h(href,params,url,m,lnum['n'])
                appends.append(app)
                return ret
        else:
            # МНЕ БЛЯТЬ ССАНО СТЫДНО ЗА ЭТОТ КОД. ОН БУДЕТ ВЫКИНУТ НАХУЙ СКОРО СОВСЕМ.
            ulm = _USER_LINK_RE.match(href)
            if ulm:
                url = '@'+ulm.group(1)
            else:
                plm = _MSG_LINK_RE.match(href)
                if plm:
                    url = '#' + plm.group(1) + ('/'+plm.group(2) if plm.group(2) else '')
            return u'<a href="%s"%s>%s</a>' % (href, params, url)

    def make_user(m):
        return widgets.userl(m.group(1).lower())
    def make_msg(m):
        return widgets.msgl(m.group(1).upper())
    # First HTML-escape so that our strings are all safe.
    # The regex is modified to avoid character entites other than &amp; so
    # that we won't pick up &quot;, etc.
    text = _unicode(xhtml_escape(text))
    restext = _USER_RE.sub((lambda m: 'http://bnw.im/u/'+m.group(1)),text)
    restext = _MSG_RE.sub((lambda m: 'http://bnw.im/p/'+m.group(1)+('#'+m.group(2) if m.group(2) else '')),restext)
    restext = _URL_RE.sub(make_link, restext)
    #restext = _MSG_RE.sub(make_msg,restext)
    if appends:
        return restext+('<div class="imgpreviews">%s</div>' % (''.join(appends),))
    else:
        return restext

