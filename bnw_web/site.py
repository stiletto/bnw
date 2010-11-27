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
#import tornado.escape
import logging,traceback
import simplejson as json
import txmongo
import os,random,time
import escape
from widgets import widgets
import PyRSS2Gen
import websocket_site
from datetime import datetime

from tornado.options import define, options

import bnw_core.bnw_objects as objs
import bnw_core.post as post
from bnw_core.base import get_db
from base import BnwWebHandler, TwistedHandler
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

class UserHandler(BnwWebHandler):
    templatename='user.html'
    @defer.inlineCallbacks
    def respond(self,username,page=0):
        f = txmongo.filter.sort(txmongo.filter.DESCENDING("date"))
        user=(yield objs.User.find_one({'name': username}))
        page=int(page)
        messages=(yield objs.Message.find({'user': username},filter=f,limit=20,skip=20*page))
        
        format=self.get_argument("format","")
        if format=='rss':
            rss_items=[PyRSS2Gen.RSSItem(author=username,description=msg['text']) for msg in messages]
            rss_feed=PyRSS2Gen.RSS2(title='Поток сознания @%s' % username,
                        link='http://bnw.blasux.ru'+widgets.user_url(username),
                        description=None,
                        docs=None,
                        items=rss_items)
            defer.returnValue(rss_feed.to_xml(encoding='utf-8'))
        elif format=='json':
            json_messages=[message.filter_fields() for message in messages]
            defer.returnValue(json.dumps(json_messages,ensure_ascii=False))
        else:
            defer.returnValue({
                'username': username,
                'user': user,
                'messages': messages,
                'page': page,
            })


class UserInfoHandler(BnwWebHandler,AuthMixin):
    templatename='userinfo.html'
    @defer.inlineCallbacks
    def respond(self,username):
        user=yield objs.User.find_one({'name': username})
        subscribers=yield objs.Subscription.find({'target':username,'type':'sub_user'})
        messages_count=int((yield objs.Message.count({'user': username})))
        defer.returnValue({
            'username': username,
            'user': user,
            'regdate': time.ctime(user['regdate']) if user else '',
            'messages_count': messages_count,
            'subscribers': subscribers,
        })


class MainHandler(BnwWebHandler):
    templatename='main.html'
    @defer.inlineCallbacks
    def respond(self,page=0):
        f = txmongo.filter.sort(txmongo.filter.DESCENDING("date"))
        page=int(page)
        messages=(yield objs.Message.find({},filter=f,limit=20,skip=20*page))
        uc=(yield objs.User.count())
        defer.returnValue({
            'messages': messages,
            'users_count':int(uc),
            'page': page,
        })

class PostHandler(BnwWebHandler,AuthMixin):
    templatename='post.html'
    @requires_auth
    @defer.inlineCallbacks
    def respond_post(self):
        tags=[i[:128] for i in self.get_argument("tags","").split(",",5)[:5]]
        clubs=[i[:128] for i in self.get_argument("clubs","").split(",",5)[:5]]
        text=self.get_argument("text","")
        user = yield self.get_auth_user()
        result = yield post.postMessage(user,tags,clubs,text)
        if isinstance(result,tuple):
            (msg_id,qn,recs) = result
            self.redirect('/p/'+msg_id)
            defer.returnValue('')
        else:
            defer.returnValue(result)
    @requires_auth
    @defer.inlineCallbacks
    def respond(self):
        user = yield self.get_auth_user()
        defer.returnValue({ 'auth_user': user})


class CommentHandler(BnwWebHandler,AuthMixin):
    templatename='comment.html'
    @requires_auth
    @defer.inlineCallbacks
    def respond_post(self):
        msg=self.get_argument("msg","")
        comment=self.get_argument("comment","")
        text=self.get_argument("text","")
        noredir=self.get_argument("noredir","")
        user = yield self.get_auth_user()
        result = yield post.postComment(msg,comment,text,user)
        if isinstance(result,tuple):
            (msg_id,qn,recs) = result
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

def get_site():
    settings={
        'template_path':os.path.join(os.path.dirname(__file__), "templates")
    }
    application = tornado.web.Application([
#        (r"/posts/(.*)", MessageHandler),
        (r"/p/([A-Z0-9]+)/?", MessageHandler),
        #(r"/p/([A-Z0-9]+)/ws", MessageWsHandler),
        (r"/u/([0-9a-z_-]+)/?", UserHandler),
        (r"/u/([0-9a-z_-]+)/info/?", UserInfoHandler),
        (r"/u/([0-9a-z_-]+)/pg([0-9]+)/?", UserHandler),
        (r"/", MainHandler),
        (r"/pg([0-9]+)", MainHandler),
        (r"/login", LoginHandler),
        (r"/post", PostHandler),
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
