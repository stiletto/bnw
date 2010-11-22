# -*- coding: utf-8 -*-
from twisted.internet import epollreactor
#epollreactor.install()
from twisted.internet import reactor
from twisted.internet import interfaces, defer

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

from tornado.options import define, options

import bnw_core.bnw_objects as objs
from bnw_core.base import get_db
define("port", default=8888, help="run on the given port", type=int)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world!")

class TwistedHandler(tornado.web.RequestHandler):
    def writeandfinish(self,text):
        self.write(text)
        self.finish()
    def errorfinish(self,text):
        print 'ALARM'
        if isinstance(text,Exception):
            self.write(str(text))
        else:
            self.write(str(text))
        self.finish()
    def json_fuckup(self,dct):
        if isinstance(dct,objs.MongoObject):
            return dct.doc
        if isinstance(dct,txmongo.ObjectId):
            return str(dct)
        else:
            raise TypeError(str(type(dct)))
    @tornado.web.asynchronous
    def get(self,*args,**kwargs):
        try:
            self.respond(*args,**kwargs).addCallbacks(self.writeandfinish,self.errorfinish)
        except Exception:
            self.write(traceback.format_exc())
            self.finish()


class MessageHandler(TwistedHandler):
    @defer.inlineCallbacks
    def respond(self,query):
        f = txmongo.filter.sort(txmongo.filter.DESCENDING("date"))
        shitres=list((yield objs.Message.find(limit=20,filter=f)))
        defer.returnValue(json.dumps(shitres,default=self.json_fuckup,indent=4))

ranq=(
    'Где блекджек, где мои шлюхи? Ничерта не работает!',
    'Здраствуйте. Я, Кирилл. Хотел бы чтобы вы сделали сервис, микроблог суть такова...',
    u'Шлюхи без блекджека, блекджек без шлюх.',
    u'Бабушка, смотри, я сделал двач!',
    u'БЕГЕМОТИКОВ МОЖНО!',
    u'ビリャチピスデツナフイ',
    u'Я и мой ёбаный кот на фоне ковра.',
    u'''\u0428\u0300\u0310\u0314\u0301\u033e\u0303\u0352\u0308\u0314\u030e\u0334\u035c\u0334\u0341\u0341\u031c\u0325\u034d\u0355\u033c\u0319\u0331\u0359\u034e\u034d\u0318\u0440\u0367\u0364\u034b\u0305\u033d\u0367\u0308\u0310\u033d\u0306\u0310\u034b\u0364\u0366\u036c\u035b\u0303\u0311\u035e\u0327\u031b\u035e\u033a\u0356\u0356\u032f\u0316\u0438\u0312\u0365\u0364\u036f\u0342\u0363\u0310\u0309\u0311\u036b\u0309\u0311\u0489\u031b\u034f\u0338\u033b\u0355\u0347\u035a\u0324\u0355\u0345\u032f\u0331\u0333\u0349\u0444\u0314\u0343\u0301\u031a\u030d\u0357\u0362\u0321\u035e\u0334\u0334\u031f\u031e\u0359\u0319\u033b\u034d\u0326\u0345\u0354\u0324\u031e\u0442\u0310\u036b\u0302\u034a\u0304\u0303\u0365\u036a\u0328\u034f\u035c\u035c\u032b\u033a\u034d\u031e\u033c\u0348\u0329\u0325\u031c\u0354\u044b\u0305\u0351\u034c\u0352\u036b\u0352\u0300\u0365\u0350\u0364\u0305\u0358\u0315\u0338\u0334\u0331\u033a\u033c\u0320\u0326\u034d\u034d\u034d\u0331\u0316\u0354\u0316\u0331\u0349.\u0366\u0306\u0300\u0311\u030c\u036e\u0367\u0363\u036f\u0314\u0302\u035f\u0321\u0335\u0341\u0334\u032d\u033c\u032e\u0356\u0348\u0319\u0356\u0356\u0332\u032e\u032c\u034d\u0359\u033c\u032f\u0326\u032e\u032e\u0433\u034c\u036e\u030f\u0308\u0342\u036f\u031a\u0489\u0340\u0358\u031b\u035e\u0319\u032c\u0318\u0332\u0317\u0347\u0355\u0320\u0319\u0345\u0359\u033c\u0329\u035a\u043e\u0313\u0364\u033d\u0352\u030b\u0309\u0300\u0302\u0304\u0312\u0343\u030a\u0368\u035b\u0301\u030c\u0364\u0302\u0337\u0340\u0360\u0325\u032f\u0318\u0432\u0312\u0352\u0343\u030f\u031a\u0313\u0336\u0489\u031b\u035c\u0319\u0318\u033a\u0330\u032e\u033c\u031f\u033c\u0325\u031f\u0318\u0320\u031c\u043d\u033f\u0314\u0303\u0368\u0351\u0338\u0337\u0338\u0332\u031d\u0348\u0359\u0330\u031f\u033b\u031f\u0330\u031c\u031f\u0317\u034e\u033b\u033b\u034d\u043e\u0314\u0300\u030b\u036b\u0307\u033f\u0310\u036b\u034c\u0357\u0369\u0489\u0315\u0328\u0361\u035c\u031c\u0319\u0319\u0348\u034d\u032e\u032e\u033c\u0319\u0318\u031e''',
)

class BnwWebHandler(TwistedHandler):
    def render(self,templatename,**kwargs):
        global ranq
        defargs={
            'linkify': escape.linkify,
            'ranq': random.choice(ranq),
            'w': widgets,
        }
        defargs.update(kwargs)
        return super(BnwWebHandler,self).render(templatename,**defargs)

    def writeandfinish(self,text):
        if isinstance(text,dict):
            self.render(self.templatename,**text)
        else:
            super(BnwWebHandler,self).writeandfinish(text)

class MessageHandler(BnwWebHandler):
    templatename='message.html'
    @defer.inlineCallbacks
    def respond(self,msgid):
        f = txmongo.filter.sort(txmongo.filter.ASCENDING("date"))
        msg=(yield objs.Message.find_one({'id': msgid}))
        comments=(yield objs.Comment.find({'message': msgid},filter=f))
        defer.returnValue({
            'msgid': msgid,
            'msg': msg,
            'comments': comments,
        })

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
        else:
            defer.returnValue({
                'username': username,
                'user': user,
                'messages': messages,
                'page': page,
            })

class UserInfoHandler(BnwWebHandler):
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

def get_site():
    settings={
        'template_path':os.path.join(os.path.dirname(__file__), "templates")
    }
    application = tornado.web.Application([
#        (r"/posts/(.*)", MessageHandler),
        (r"/p/([A-Z0-9]+)/?", MessageHandler),
        (r"/u/([0-9a-z_-]+)/?", UserHandler),
        (r"/u/([0-9a-z_-]+)/info/?", UserInfoHandler),
        (r"/u/([0-9a-z_-]+)/pg([0-9]+)/?", UserHandler),
        (r"/", MainHandler),
        (r"/pg([0-9]+)", MainHandler),
    ],**settings)

    site = tornado.twister.TornadoSite(application)
    return site

def main():
    tornado.options.parse_command_line()
    site = get_site()
    reactor.listenTCP(options.port, site)

    reactor.run()

if __name__ == "__main__":
    main()
