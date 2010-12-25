# -*- coding: utf-8 -*-
from twisted.internet import epollreactor
#epollreactor.install()
from twisted.internet import reactor
from twisted.internet import interfaces, defer
from twisted.web.server import Site, NOT_DONE_YET
from twisted.web.resource import Resource, NoResource

import tornado.options
import tornado.twister
import tornado.web
import tornado.escape
import logging,traceback
import simplejson as json
import txmongo
import os,random,time
import escape
from widgets import widgets
import rss
import base64
import websocket_site
from datetime import datetime

from tornado.options import define, options

import bnw_core.bnw_objects as objs
import bnw_core.post as post
import bnw_core.base
from bnw_core.base import get_db,get_fs
from bnw_xmpp.command_show import cmd_feed

from base import BnwWebHandler, TwistedHandler, BnwWebRequest
from auth import LoginHandler, requires_auth, AuthMixin
define("port", default=8888, help="run on the given port", type=int)

class MessageHandler(BnwWebHandler,AuthMixin):
    templatename='message.html'
    @defer.inlineCallbacks
    def respond(self,msgid):
        user = yield self.get_auth_user()
        f = txmongo.filter.sort(txmongo.filter.ASCENDING("date"))
        msg=(yield objs.Message.find_one({'id': msgid}))
        comments=(yield objs.Comment.find({'message': msgid},filter=f))
        defer.returnValue({
            'msgid': msgid,
            'msg': msg,
            'auth_user': user,
            'comments': comments,
        })

class MessageWsHandler(websocket_site.RoutedWebSocketHandler):
    def openSocket(self,msgid):
        self.etype='comments-'+msgid
        post.register_listener(self.etype,id(self),self.deliverComment)
        print 'Opened connection %d' % id(self)
    def deliverComment(self,comment):
        print 'Delivered comment.',comment
        self.write(json.dumps(comment))
    def connectionLost(self,reason):
        post.unregister_listener(self.etype,id(self))
        print 'Closed connection %d' % id(self)


def get_page(self):
    ra = self.request.args
    rv = ra.get('page',['0'])[0]
    if rv.isdigit():
        return int(rv)
    return 0    

class UserHandler(BnwWebHandler):
    templatename='user.html'
    @defer.inlineCallbacks
    def respond(self,username,tag=None):
        f = txmongo.filter.sort(txmongo.filter.DESCENDING("date"))
        user = (yield objs.User.find_one({'name': username}))
        page = get_page(self)
        qdict = { 'user': username }
        if tag:
            tag = tornado.escape.url_unescape(tag)
            qdict['tags'] = tag
        print qdict
        messages=(yield objs.Message.find(qdict,filter=f,limit=20,skip=20*page))
        
        format=self.get_argument("format","")
        if format=='rss':
            self.set_header("Content-Type", 'application/rss+xml; charset=UTF-8')
            defer.returnValue(rss.message_feed(messages,
                        link=widgets.user_url(username),
                        title='Поток сознания @%s' % username))
        elif format=='json':
            json_messages=[message.filter_fields() for message in messages]
            defer.returnValue(json.dumps(json_messages,ensure_ascii=False))
        else:
            defer.returnValue({
                'username': username,
                'user': user,
                'messages': messages,
                'page': page,
                'tag' : tag,
            })


class UserInfoHandler(BnwWebHandler,AuthMixin):
    templatename='userinfo.html'
    @defer.inlineCallbacks
    def respond(self,username):
        user = yield objs.User.find_one({'name': username})
        subscribers = set([x['user'] for x in 
                    (yield objs.Subscription.find({'target':username,'type':'sub_user'}))])
        subscriptions = set([x['target'] for x in 
                    (yield objs.Subscription.find({'user':username,'type':'sub_user'}))])
        friends = list(subscribers & subscriptions)
        friends.sort()
        subscribers_only = list(subscribers - subscriptions)
        subscribers_only.sort()
        subscriptions_only = list(subscriptions - subscribers)
        subscriptions_only.sort()
        messages_count = int((yield objs.Message.count({'user': username})))
        defer.returnValue({
            'username': username,
            'user': user,
            'regdate': time.ctime(user['regdate']) if user else '',
            'messages_count': messages_count,
            'subscribers': subscribers_only,
            'subscriptions': subscriptions_only,
            'friends': friends,
        })


class MainHandler(BnwWebHandler):
    templatename='main.html'
    @defer.inlineCallbacks
    def respond(self,club=None,tag=None):
        f = txmongo.filter.sort(txmongo.filter.DESCENDING("date"))

        page = get_page(self)
        qdict = {}
        if tag:
            tag = tornado.escape.url_unescape(tag)
            qdict['tags'] = tag
        if club:
            club = tornado.escape.url_unescape(club)
            qdict['clubs'] = club

        messages=(yield objs.Message.find(qdict,filter=f,limit=20,skip=20*page))
        uc=(yield objs.User.count())
        format=self.get_argument("format","")

        if format=='rss':
            self.set_header("Content-Type", 'application/rss+xml; charset=UTF-8')
            defer.returnValue(rss.message_feed(messages,
                        link=bnw_core.base.config.webui_base,
                        title='Коллективное бессознательное BnW'))

        elif format=='json':
            json_messages=[message.filter_fields() for message in messages]
            defer.returnValue(json.dumps(json_messages,ensure_ascii=False))

        else:
            defer.returnValue({
                'messages': messages,
                'users_count':int(uc),
                'page': page,
            })

class FeedHandler(BnwWebHandler,AuthMixin):
    templatename='feed.html'
    @requires_auth
    @defer.inlineCallbacks
    def respond(self,page=0):
        req=BnwWebRequest((yield self.get_auth_user()))
        result = yield cmd_feed(req)
        defer.returnValue({
            'result': result,
        })

class BlogHandler(BnwWebHandler,AuthMixin):
    @requires_auth
    @defer.inlineCallbacks
    def respond(self,page=0):
        user=yield self.get_auth_user()
        self.redirect(str('/u/'+user['name']))


class PostHandler(BnwWebHandler,AuthMixin):
    templatename='post.html'
    @requires_auth
    @defer.inlineCallbacks
    def respond_post(self):
        tags=[i[:128] for i in self.get_argument("tags","").split(",",5)[:5]]
        clubs=[i[:128] for i in self.get_argument("clubs","").split(",",5)[:5]]
        text=self.get_argument("text","")
        user = yield self.get_auth_user()
        ok,result = yield post.postMessage(user,tags,clubs,text)
        if ok:
            (msg_id,qn,recs) = result
            self.redirect('/p/'+msg_id)
            defer.returnValue('')
        else:
            defer.returnValue(result.get('desc','Error'))
    @requires_auth
    @defer.inlineCallbacks
    def respond(self):
        user = yield self.get_auth_user()
        default_text = self.get_argument("url","")
        defer.returnValue({ 'auth_user': user, 'default_text': default_text })


class CommentHandler(BnwWebHandler,AuthMixin):
    templatename='comment.html'
    @requires_auth
    @defer.inlineCallbacks
    def respond_post(self):
        msg=self.get_argument("msg","")
        comment=self.get_argument("comment","")
        if comment:
            comment=msg+"/"+comment
        text=self.get_argument("text","")
        noredir=self.get_argument("noredir","")
        user = yield self.get_auth_user()
        ok,result = yield post.postComment(msg,comment,text,user)
        if ok:
            (msg_id,num,qn,recs) = result
            if noredir:
                defer.returnValue('Posted with '+msg_id)
            else:
                redirtarget='/p/'+msg_id.replace('/','#')
                # странная хуйня с твистедом или еще чем-то
                # если в редиректе unicode-объект - реквест не финиширует
                self.redirect(str(redirtarget))
                defer.returnValue('')
        else:
            defer.returnValue(result)

class OexchangeHandler(BnwWebHandler):
    templatename='oexchange.xrd'
    @defer.inlineCallbacks
    def respond(self):
        self.set_header("Content-Type", "application/xrd+xml")
        defer.returnValue({})
        yield

class HostMetaHandler(BnwWebHandler):
    templatename='oexchange-host-meta'
    @defer.inlineCallbacks
    def respond(self):
        self.set_header("Content-Type", "application/xrd+xml")
        defer.returnValue({})
        yield

emptypng=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAQMAAAAl21bKAAAAAXNSR0IDN8dNUwAAAANQTFRF////p8QbyAAAAAlwSFlzAAAPYQAAD2EBqD+naQAAABZ6VFh0YXV0aG9yAAB42gtOLUpPrQQACDECcKiD3nQAAAAKSURBVAjXY2AAAAACAAHiIbwzAAAAAElFTkSuQmCC')

class AvatarHandler(BnwWebHandler):
    @defer.inlineCallbacks
    def respond(self,username):
        user=(yield objs.User.find_one({'name': username}))
        if not (user and 'avatar' in user):
            self.set_header("Content-Type", "image/png")
            defer.returnValue(emptypng)
        fs = (yield get_fs('avatars'))
        # воркэраунд недопила в txmongo. TODO: зарепортить или починить
        doc = yield fs._GridFS__files.find_one({'_id':user['avatar'][0]})
        avatar = yield fs.get(doc)
        avatar_data = yield avatar.read()
        self.set_header("Content-Type", user['avatar'][1])
        defer.returnValue(avatar_data)

def get_site():
    settings={
        "template_path":os.path.join(os.path.dirname(__file__), "templates"),
        "xsrf_cookies": True,
        "static_path":  os.path.join(os.path.dirname(__file__), "static"),
    }
    application = tornado.web.Application([
#        (r"/posts/(.*)", MessageHandler),
        (r"/p/([A-Z0-9]+)/?", MessageHandler),
        #(r"/p/([A-Z0-9]+)/ws", MessageWsHandler),
        (r"/u/([0-9a-z_-]+)/?", UserHandler),
        (r"/u/([0-9a-z_-]+)/?", UserHandler),
        (r"/u/([0-9a-z_-]+)/avatar/?", AvatarHandler),
        (r"/u/([0-9a-z_-]+)/info/?", UserInfoHandler),
        (r"/u/([0-9a-z_-]+)/t/(.*)/?", UserHandler),
        (r"/", MainHandler),
        (r"/t/()(.*)/?", MainHandler),
        (r"/c/(.*)()/?", MainHandler),
        (r"/oexchange.xrd", OexchangeHandler),
        (r"/.well-known/host-meta", HostMetaHandler),
        (r"/login", LoginHandler),
        (r"/post", PostHandler),
        (r"/feed", FeedHandler),
        (r"/blog", BlogHandler),
        (r"/comment", CommentHandler),
    ],**settings)

    ws_application = websocket_site.WebSocketApplication([
        (r"/p/([A-Z0-9]+)/?", MessageWsHandler),
    ])
    #site = tornado.twister.TornadoSite(application)
    site = websocket_site.CombinedSite(application,ws_application)
    return site

def main():
    tornado.options.parse_command_line()
    site = get_site()
    reactor.listenTCP(options.port, site)

    reactor.run()

if __name__ == "__main__":
    main()
