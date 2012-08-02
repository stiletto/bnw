import tornado.web
from bnw_web.base import get_defargs
from bnw_web.widgets import widgets


class Message(tornado.web.UIModule):
    def render(self, msg, full=False, username=None):
        args = get_defargs()
        args['msg'] = msg
        args['full'] = full
        args['username'] = username
        args['proto'] = self.request.protocol
        return self.render_string('module-message.html', **args)


class Comment(tornado.web.UIModule):
    def render(self, comment):
        args = get_defargs()
        args['comment'] = comment
        args['proto'] = self.request.protocol
        return self.render_string('module-comment.html', **args)
