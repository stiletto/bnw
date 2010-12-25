# -*- coding: utf-8 -*-
import tornado.escape
import datetime
import bnw_core.base

def runums(n,d1,d2,d5):
    l=n%10
    if 10<n<15:
        return d5
    elif l==1:
        return d1
    elif 1<l<5:
        return d2
    else:
        return d5

class Widgets(object):
    def tag(self,tag,user=None):
        pars = {'tu': tornado.escape.url_escape(tag),
                't':  tornado.escape.xhtml_escape(tag[:32]),
                'u':  user, }
        if user:
            return '<a href="/u/%(u)s/t/%(tu)s" class="tag">%(t)s</a>' % pars
        else:
            return '<a href="/t/%(tu)s" class="tag">%(t)s</a>' % pars

    def club(self,club,user=None):
        pars = {'tu': tornado.escape.url_escape(club),
                't':  tornado.escape.xhtml_escape(club[:32]),
                'u':  user, }
        #if user:
        #    return '<a href="/u/%(u)s/c/%(tu)s" class="tag">%(t)s</a>' % pars
        #else:
        return '<a href="/c/%(tu)s" class="club">%(t)s</a>' % pars
    def tags(self,tags,clubs,user=None):
        return '<div class="tags"> '+' '.join(self.club(c,user) for c in clubs)+' '+' '.join(self.tag(t,user) for t in tags)+' </div>'
    def user_url(self,name):
        return bnw_core.base.config.webui_base+'u/%(u)s' % {'u':name}
    def post_url(self,name):
        return bnw_core.base.config.webui_base+'p/%(u)s' % {'u':name}
    def userl(self,name):
        return '<a href="/u/%(u)s" class="usrid">@%(u)s</a>' % {'u':name}
    def msgl(self,msg):
        return '<a href="/p/%(u)s" class="msgid">#%(n)s</a>' % {'u':msg.replace('/','#'),'n':msg}
    def time(self,timestamp):
        dn=datetime.datetime.utcnow()
        dt=datetime.datetime.utcfromtimestamp(timestamp)
        dd=dn-dt
        res=''
        if dd.days>0:
            res=str(dd.days)+' '+runums(dd.days,'день','дня','дней')
        else:
            if dd.seconds>3600:
                hours=dd.seconds/3600
                res=str(hours)+' '+runums(hours,'час','часа','часов')
            elif dd.seconds>60:
                minutes=dd.seconds/60
                res=str(minutes)+' '+runums(minutes,'минуту','минуты','минут')
            else:
                res=str(dd.seconds)+' '+runums(dd.seconds,'секунду','секунды','секунд')
        return res+' назад'
        #.strftime('%d.%m.%Y %H:%M:%S')
widgets=Widgets()
