import tornado.web
from bnw.web.base import get_defargs
from bnw.web.widgets import widgets


class Message(tornado.web.UIModule):
    def render(self, msg, full=False, username=None, secure=False):
        args = get_defargs()
        args['msg'] = msg
        args['full'] = full
        args['username'] = username
        args['secure'] = secure
        return self.render_string('module-message.html', **args)


class Comment(tornado.web.UIModule):
    def render(self, comment, secure=False):
        args = get_defargs()
        args['comment'] = comment
        args['secure'] = secure
        return self.render_string('module-comment.html', **args)
