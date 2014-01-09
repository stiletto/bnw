import tornado.web
from bnw.web.base import get_defargs
from bnw.web.widgets import widgets


class Message(tornado.web.UIModule):
    def render(self, msg, full=False, username=None):
        args = get_defargs()
        args['msg'] = msg
        args['full'] = full
        args['username'] = username
        return self.render_string('module-message.html', **args)


class Comment(tornado.web.UIModule):
    def render(self, comment):
        args = get_defargs()
        args['comment'] = comment
        return self.render_string('module-comment.html', **args)
