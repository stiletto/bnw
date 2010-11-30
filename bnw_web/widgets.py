# -*- coding: utf-8 -*-
import tornado.escape
import datetime

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
    def tag(self,tag):
        return '<a href="#" class="tag">%(u)s</a>' % {'u':tornado.escape.xhtml_escape(tag[:32])}
    def club(self,club):
        return '<a href="#" class="club">%(u)s</a>' % {'u':tornado.escape.xhtml_escape(club[:32])}
    def tags(self,tags,clubs):
        return '<div class="tags"> '+' '.join(self.club(c) for c in clubs)+' '+' '.join(self.tag(t) for t in tags)+' </div>'
    def user_url(self,name):
        return '/u/%(u)s' % {'u':name}
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
