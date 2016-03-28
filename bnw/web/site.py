# -*- coding: utf-8 -*-
from twisted.internet import reactor
from twisted.internet import interfaces, defer
from twisted.web.resource import Resource, NoResource

import tornado.options
import tornado.httpserver
import tornado.web
import tornado.websocket
import tornado.escape
import logging
import traceback
import json
#import txmongo
import os
from widgets import widgets
import uimodules
import rss
import base64
import math
import time

from tornado.options import define, options

import bnw.core.bnw_objects as objs
import bnw.core.post as post
import bnw.core.base
from bnw.core.bnw_mongo import get_db
from bnw.core.bnw_gridfs import get_fs
from bnw.handlers.command_show import cmd_feed, cmd_today
from bnw.handlers.command_clubs import cmd_clubs, cmd_tags
from bnw.handlers.command_userinfo import cmd_userinfo

from bnw.web.base import BnwWebHandler, BnwWebRequest
from bnw.web.auth import LoginHandler, LogoutHandler, requires_auth, AuthMixin
from bnw.web.api import ApiHandler
define("port", default=8888, help="run on the given port", type=int)

wscount = 0


class WsHandler(tornado.websocket.WebSocketHandler):
    """Helper class for websocket handlers.
    Register listeners and send new events to clients.
    Unregister listeners on close.
    """

    def get_handlers(self, *args):
        return ()

    def open(self, *args):
        self.version = self.request.arguments.get('v', ['0'])[0]
        self.handlers = self.get_handlers(*args)
        for etype, handler in self.handlers:
            post.register_listener(etype, id(self), handler)
        global wscount
        wscount += 1
        print 'Opened connection %d (v%s). %d connections. %s' % (id(self), self.version, wscount, self.request.path)

    def on_close(self):
        for etype, _ in self.handlers:
            post.unregister_listener(etype, id(self))
        global wscount
        wscount -= 1
        print 'Closed connection %d. %d connections active.' % (id(self), wscount)


class MainWsHandler(WsHandler, AuthMixin):
    """Deliver new events on main page via websockets."""

    def get_handlers(self):
        if self.version == '2':
            return (
                ('new_message', self.new_message),
                ('del_message', self.del_message),
                ('upd_comments_count', self.upd_comments_count),
                ('upd_recommendations_count', self.upd_recommendations_count),
            )
        else:
            return (
                ('new_message', self.new_message_compat),
            )

    @defer.inlineCallbacks
    def new_message(self, msg):
        user = yield self.get_auth_user()
        if user and ['user', msg['user']] in user.get('blacklist', []):
            return
        html = uimodules.Message(self).render(msg)
        msg = msg.copy()
        if user:
            msg['subscribed'] = user['name'] == msg['user']
        msg.update(dict(type='new_message', html=html))
        self.write_message(json.dumps(msg))

    @defer.inlineCallbacks
    def new_message_compat(self, msg):
        user = yield self.get_auth_user()
        if user and ['user', msg['user']] in user.get('blacklist', []):
            return
        self.write_message(json.dumps(msg))

    def del_message(self, msg_id):
        self.write_message(json.dumps({'type': 'del_message', 'id': msg_id}))

    def upd_comments_count(self, msg_id, num):
        self.write_message(json.dumps({
            'type': 'upd_comments_count', 'id': msg_id, 'num': num}))

    def upd_recommendations_count(self, msg_id, num, recommendations):
        self.write_message(json.dumps({
            'type': 'upd_recommendations_count', 'id': msg_id, 'num': num,
            'recommendations': recommendations}))

    def check_origin(self, origin):
        return True


class UserWsHandler(MainWsHandler):
    """Deliver new events on user page via websockets."""

    def get_handlers(self, user):
        return (
            ('new_message_on_user_' + user, self.new_message),
            ('del_message_on_user_' + user, self.del_message),
            # TODO: Should we update only user's messages?
            ('upd_comments_count', self.upd_comments_count),
            ('upd_recommendations_count', self.upd_recommendations_count),
        )

    def check_origin(self, origin):
        return True


class CommentsWsHandler(WsHandler):
    """Deliver new comments via websockets."""

    def get_handlers(self):
        return (
            ('new_comment', self.new_comment),
        )

    def new_comment(self, comment):
        self.write_message(json.dumps(comment))

    def check_origin(self, origin):
        return True


class MessageWsHandler(MainWsHandler):
    """Deliver new events on message page via websockets."""

    def get_handlers(self, msgid):
        if self.version == '2':
            return (
                ('new_comment_in_' + msgid, self.new_comment),
                ('del_comment_in_' + msgid, self.del_comment),
                ('upd_comments_count_in_' + msgid, self.upd_comments_count),
                ('upd_recommendations_count_in_' + msgid,
                 self.upd_recommendations_count),
            )
        else:
            return (
                ('new_comment_in_' + msgid, self.new_comment_compat),
            )

    @defer.inlineCallbacks
    def new_comment(self, comment):
        user = yield self.get_auth_user()
        if user and ['user', comment['user']] in user.get('blacklist', []):
            return
        html = uimodules.Comment(self).render(comment)
        comment = comment.copy()
        comment.update(dict(type='new_comment', html=html))
        self.write_message(json.dumps(comment))

    def new_comment_compat(self, comment):
        self.write_message(json.dumps(comment))

    def del_comment(self, comment_id):
        self.write_message(json.dumps(
            {'type': 'del_comment', 'id': comment_id}))

    def check_origin(self, origin):
        return True



def get_page(self):
    ra = self.request.arguments
    rv = ra.get('page', ['0'])[0]
    if rv.isdigit():
        rv = int(rv)
        return rv if isinstance(rv, int) else 0  # no long here
    return 0


@defer.inlineCallbacks
def is_hasmes(qdict, page):
    """Return True if summary page count bigger than given
    (given page numbering starting from 0).
    """
    count = yield objs.Message.count(qdict)
    defer.returnValue(int(math.ceil(count / 20.0)) > page + 1)


class UserHandler(BnwWebHandler, AuthMixin):
    templatename = 'user.html'

    @defer.inlineCallbacks
    def respond(self, username, reco=None, tag=None):
        _ = yield self.get_auth_user()
        f = [("date", -1)]
        user = (yield objs.User.find_one({'name': username}))
        page = get_page(self)

        if reco == "recommendations":
            qdict = {'recommendations': username}
        elif reco == "all":
            qdict = {'$or': [{'user': username}, {
                'recommendations': username}]}
        else:
            qdict = {'user': username}

        if tag:
            tag = tornado.escape.url_unescape(tag)
            qdict['tags'] = tag
        messages = list((yield objs.Message.find_sort(qdict, sort=f, limit=20, skip=20 * page)))
        hasmes = yield is_hasmes(qdict, page)

        format = self.get_argument("format", "")
        if format == 'rss':
            self.set_header(
                "Content-Type", 'application/rss+xml; charset=UTF-8')
            defer.returnValue(rss.message_feed(messages,
                                               link=widgets.user_url(username),
                                               title='Поток сознания @%s' % username))
        elif format == 'json':
            json_messages = [message.filter_fields() for message in messages]
            defer.returnValue(json.dumps(json_messages, ensure_ascii=False))
        else:
            self.set_header("Cache-Control", "max-age=1")
            defer.returnValue({
                'username': username,
                'user': user,
                'messages': messages,
                'page': page,
                'tag': tag,
                'hasmes': hasmes,
            })


class UserRecoHandler(BnwWebHandler, AuthMixin):
    templatename = 'user.html'

    @defer.inlineCallbacks
    def respond(self, username, tag=None):
        _ = yield self.get_auth_user()
        f = [("date", -1)]
        user = (yield objs.User.find_one({'name': username}))
        page = get_page(self)
        qdict = {'recommendations': username}
        if tag:
            tag = tornado.escape.url_unescape(tag)
            qdict['tags'] = tag
        messages = list((yield objs.Message.find_sort(qdict, sort=f, limit=20, skip=20 * page)))
        hasmes = yield is_hasmes(qdict, page)

        self.set_header("Cache-Control", "max-age=1")
        defer.returnValue({
            'username': username,
            'user': user,
            'messages': messages,
            'page': page,
            'tag': tag,
            'hasmes': hasmes,
        })


class UserInfoHandler(BnwWebHandler, AuthMixin):
    templatename = 'userinfo.html'

    @defer.inlineCallbacks
    def respond(self, user):
        req = BnwWebRequest((yield self.get_auth_user()))
        self.set_header('Cache-Control', 'max-age=10')
        defer.returnValue((yield cmd_userinfo(req, user)))


class MessageHandler(BnwWebHandler, AuthMixin):
    templatename = 'message.html'

    @defer.inlineCallbacks
    def respond(self, msgid):
        user = yield self.get_auth_user()
        f = [("date", 1)]
        msg = (yield objs.Message.find_one({'id': msgid}))
        qdict = {'message': msgid}
        if user:
            bl = []
            for e in user.get('blacklist', []):
                if e[0] == 'user':
                    bl.append(e[1])
            if bl:
                qdict['user'] = {'$nin': bl}
            is_subscribed = yield objs.Subscription.count({
                'user': user['name'],
                'type': 'sub_message',
                'target': msgid,
            })
        else:
            is_subscribed = False
        # TODO: Converting generator to list may be inefficient.
        comments = list((yield objs.Comment.find(qdict, sort=f, limit=10000)))
        self.set_header("Cache-Control", "max-age=5")
        if not msg:
            self.set_status(404)
        defer.returnValue({
            'msgid': msgid,
            'msg': msg,
            'auth_user': user,
            'comments': comments,
            'is_subscribed': is_subscribed,
        })


class MainHandler(BnwWebHandler, AuthMixin):
    templatename = 'main.html'

    @defer.inlineCallbacks
    def respond(self, club=None, tag=None):
        f = [("date", -1)]

        user = yield self.get_auth_user()

        page = get_page(self)
        qdict = {}
        if tag:
            tag = tornado.escape.url_unescape(tag, plus=False)
            qdict['tags'] = tag
        if club:
            club = tornado.escape.url_unescape(club, plus=False)
            qdict['clubs'] = club
        if user:
            bl = []
            for e in user.get('blacklist', []):
                if e[0] == 'user':
                    bl.append(e[1])
            if bl:
                qdict['user'] = {'$nin': bl}

        messages = list((yield objs.Message.find_sort(qdict, sort=f, limit=20, skip=20 * page)))
        hasmes = yield is_hasmes(qdict, page)
        uc = (yield objs.User.count())
        format = self.get_argument("format", "")
        active = int((yield objs.User.count({'last_activity': {'$gt': time.time()-30*60}})))

        self.set_header("Cache-Control", "max-age=1")
        if format == 'rss':
            self.set_header(
                "Content-Type", 'application/rss+xml; charset=UTF-8')
            if self.request.protocol == "https":
                base = bnw.core.base.get_https_webui_base()
            else:
                base = bnw.core.base.get_http_webui_base()
            defer.returnValue(
                rss.message_feed(
                    messages, link=base,
                    title='Коллективное бессознательное BnW'))

        elif format == 'json':
            json_messages = [message.filter_fields() for message in messages]
            defer.returnValue(json.dumps(json_messages, ensure_ascii=False))

        else:
            req = BnwWebRequest((yield self.get_auth_user()))
            tagres = yield cmd_tags(req)
            toptags = tagres['tags'] if tagres['ok'] else []
            defer.returnValue({
                'messages': messages,
                'toptags': toptags,
                'users_count': int(uc),
                'active': active,
                'page': page,
                'tag': tag,
                'club': club,
                'hasmes': hasmes,
            })


class FeedHandler(BnwWebHandler, AuthMixin):
    templatename = 'feed.html'

    @requires_auth
    @defer.inlineCallbacks
    def respond(self):
        page = get_page(self)
        req = BnwWebRequest((yield self.get_auth_user()))
        result = yield cmd_feed(req, page=page)
        self.set_header("Cache-Control", "max-age=1")
        defer.returnValue({
            'result': result,
            'page': page,
            'hasmes': result['ok'] and len(result['messages']) == 20,
        })


class TodayHandler(BnwWebHandler, AuthMixin):
    templatename = 'today.html'

    @defer.inlineCallbacks
    def respond(self):
        req = BnwWebRequest((yield self.get_auth_user()))
        result = yield cmd_today(req, use_bl=True)
        self.set_header("Cache-Control", "max-age=300")
        defer.returnValue({
            'result': result,
        })


class ClubsHandler(BnwWebHandler, AuthMixin):
    templatename = 'clubs.html'

    @defer.inlineCallbacks
    def respond(self):
        user = yield self.get_auth_user()
        req = BnwWebRequest((yield self.get_auth_user()))
        result = yield cmd_clubs(req)
        self.set_header("Cache-Control", "max-age=3600")
        defer.returnValue({
            'result': result,
        })


class BlogHandler(BnwWebHandler, AuthMixin):
    @requires_auth
    @defer.inlineCallbacks
    def respond(self):
        user = yield self.get_auth_user()
        self.redirect(str('/u/' + user['name']))
        defer.returnValue('')


class PostHandler(BnwWebHandler, AuthMixin):
    templatename = 'post.html'

    @requires_auth
    @defer.inlineCallbacks
    def respond_post(self):
        tags = [i[:128] for i in self.get_argument("tags", "")
                .split(",", 5)[:5] if i]
        clubs = [i[:128] for i in self.get_argument("clubs", "")
                 .split(",", 5)[:5] if i]
        text = self.get_argument("text", "")
        user = yield self.get_auth_user()
        ok, result = yield post.postMessage(user, tags, clubs, text)
        if ok:
            (msg_id, qn, recs) = result
            self.redirect('/p/' + msg_id)
            defer.returnValue('')
        else:
            defer.returnValue({'error': result})

    @requires_auth
    @defer.inlineCallbacks
    def respond(self):
        user = yield self.get_auth_user()
        default_text = self.get_argument("url", "")
        if not default_text:
            default_text = self.get_argument("text", "")
        default_clubs = self.get_argument("clubs", "")
        default_tags = self.get_argument("tags", "")
        self.set_header("Cache-Control", "max-age=1")
        defer.returnValue({'auth_user': user,
                           'default_text': default_text,
                           'default_tags': default_tags,
                           'default_clubs': default_clubs,
                           'error': None})


class CommentHandler(BnwWebHandler, AuthMixin):
    templatename = 'comment.html'

    @requires_auth
    @defer.inlineCallbacks
    def respond_post(self):
        msg = self.get_argument("msg", "")
        comment = self.get_argument("comment", "")
        if comment:
            comment = msg + "/" + comment
        text = self.get_argument("text", "")
        noredir = self.get_argument("noredir", "")
        user = yield self.get_auth_user()
        ok, result = yield post.postComment(msg, comment, text, user)
        if ok:
            (msg_id, num, qn, recs) = result
            if noredir:
                defer.returnValue('Posted with ' + msg_id)
            else:
                redirtarget = '/p/' + msg_id.replace('/', '#')
                # странная хуйня с твистедом или еще чем-то
                # если в редиректе unicode-объект - реквест не финиширует
                self.redirect(str(redirtarget))
                defer.returnValue('')
        else:
            defer.returnValue({'error': result})

emptypng = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAQAAAAA3bvkkAAAAAnRSTlMAAHaTzTgAAAAKSURB'
    'VAjXY2AAAAACAAHiIbwzAAAAAElFTkSuQmCC')


class AvatarHandler(BnwWebHandler):
    @defer.inlineCallbacks
    def respond(self, username, thumb=''):
        self.set_header('Cache-Control', 'max-age=3600, public')
        self.set_header('Vary', 'Accept-Encoding')
        user = yield objs.User.find_one({'name': username})
        if not (user and user.get('avatar') and False):
            self.set_header('Content-Type', 'image/png')
            defer.returnValue(emptypng)
        if thumb:
            av_id = user['avatar'][2]
            mimetype = 'image/png'
        else:
            av_id = user['avatar'][0]
            mimetype = user['avatar'][1]
        fs = yield get_fs('avatars')
        # воркэраунд недопила в txmongo. TODO: зарепортить или починить
        doc = yield fs._GridFS__files.find_one({'_id': av_id})
        avatar = yield fs.get(doc)
        avatar_data = yield avatar.read()
        self.set_header('Content-Type', mimetype)
        defer.returnValue(avatar_data)

class SitemapHandler(BnwWebHandler):
    @defer.inlineCallbacks
    def respond(self, type_):
        self.set_header('Cache-Control', 'public')
        self.set_header('Vary', 'Accept-Encoding')

        f = [("date", -1)]
        skip = 0
        self.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n\n')
        while True:
            messages = list((yield objs.Message.find_sort({}, sort=f, fields={'id':1}, limit=20, skip=skip)))
            for message in messages:
                self.write('<url><loc>http://%s/p/%s</loc><priority>1.0</priority></url>\n' % (bnw.core.base.config.webui_base, message['id']))
            if len(messages)==0 or skip>1000:
                break
            skip += 20
        self.write('</urlset>\n')
        defer.returnValue('')

def get_site():
    settings = {
        "template_path": os.path.join(os.path.dirname(__file__), "templates"),
        "xsrf_cookies": True,
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "ui_modules": uimodules,
        "autoescape": None,
        "gzip": False,
    }
    application = tornado.web.Application([
        (r"/p/([A-Z0-9]+)/?", MessageHandler),
        (r"/p/([A-Z0-9]+)/ws/?", MessageWsHandler),
        (r"/u/([0-9a-z_-]+)(?:/(recommendations|all))?/?", UserHandler),
        (r"/u/([0-9a-z_-]+)/ws/?", UserWsHandler),
        (r"/u/([0-9a-z_-]+)/avatar(/thumb)?/?", AvatarHandler),
        (r"/u/([0-9a-z_-]+)/info/?", UserInfoHandler),
        (r"/u/([0-9a-z_-]+)(?:/(recommendations|all))?/t/(.*)/?", UserHandler),
        (r"/", MainHandler),
        (r"/ws/?", MainWsHandler),
        (r"/comments/ws/?", CommentsWsHandler),
        (r"/t/()(.*)/?", MainHandler),
        (r"/c/(.*)()/?", MainHandler),
        (r"/login", LoginHandler),
        (r"/logout", LogoutHandler),
        (r"/post", PostHandler),
        (r"/feed", FeedHandler),
        (r"/today", TodayHandler),
        (r"/clubs", ClubsHandler),
        (r"/blog", BlogHandler),
        (r"/comment", CommentHandler),
        (r"/sitemap-(messages).xml", SitemapHandler),
        (r"/api/([0-9a-z/]*)", ApiHandler),
    ], **settings)

    return tornado.httpserver.HTTPServer(application, xheaders=True)


def main():
    tornado.options.parse_command_line()
    site = get_site()
    reactor.listenTCP(options.port, site)
    reactor.run()

if __name__ == '__main__':
    main()
