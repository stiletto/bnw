# -*- coding: utf-8 -*-
import tornado.escape
import datetime

def runums(n, d1, d2, d5):
    if 10 < n < 15:
        return d5
    n = n % 10
    if n == 1:
        return d1
    elif 1 < n < 5:
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
        return '<a href="/c/%(tu)s" class="club">%(t)s</a>' % pars

    def tags(self,tags,clubs,user=None):
        return '<div class="tags"> '+' '.join(self.club(c,user) for c in clubs)+' '+' '.join(self.tag(t,user) for t in tags)+' </div>'

    def user_url(self,name):
        return '/u/%(u)s' % {'u':name}

    def post_url(self,name):
        return '/p/%(u)s' % {'u':name}

    def userl(self,name):
        return '<a href="/u/%(u)s" class="usrid">@%(u)s</a>' % {'u':name}

    def msgl(self,msg,bookmark=False):
        bm = ' rel="bookmark"' if bookmark else ''
        return '<a href="/p/%(u)s"%(bm)s class="msgid">#%(n)s</a>' % {'u':msg.replace('/','#'),'n':msg, 'bm': bm, }

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
        return '<abbr class="published" title="'+dt.strftime('%Y-%m-%dT%H:%M:%S+0000')+'">'+res+' назад</abbr>'

    def messages(self, count):
        return runums(count, u"сообщение", u"сообщения", u"сообщений")

    def comments(self, count):
        return runums(count, u"комментарий", u"комментария", u"комментариев")

    def shorttext(self,txt,maxwords=7,maxlen=70,ellipsis="..."):
        words=0
        pos=0
        lt=len(txt)
        while words<maxwords and pos<lt:
            prevpos=pos
            pos=txt.find(" ",pos+1)
            if pos==-1: pos=lt
            if pos>=maxlen:
                if ellipsis and pos<lt:
                    return txt[:prevpos]+ellipsis
                else:
                    return txt[:prevpos]
            words+=1
        if ellipsis and pos<lt:
            return txt[:pos]+ellipsis
        else:
            return txt[:pos]

widgets=Widgets()
