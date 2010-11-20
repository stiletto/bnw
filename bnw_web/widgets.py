import tornado.escape
class Widgets(object):
    def tag(self,tag):
        return '<a href="#" class="tag">%(u)s</a>' % {'u':tornado.escape.xhtml_escape(tag[:10])}
    def tags(self,tags):
        return '<div class="tags">'+' '.join(self.tag(t) for t in tags)+'</div>'
    def userl(self,name):
        return '<a href="/u/%(u)s" class="usrid">@%(u)s</a>' % {'u':name}
    def msgl(self,msg):
        return '<a href="/p/%(u)s" class="msgid">#%(n)s</a>' % {'u':msg.replace('/','#'),'n':msg}
widgets=Widgets()
