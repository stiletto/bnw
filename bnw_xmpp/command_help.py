# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

from base import *
import random


from parser_redeye import requireAuthRedeye
from parser_simplified import requireAuthSimplified

def _(s,user):
    return s


class HelpCommand(BaseCommand):

    helptext="""
1. Постинг сообщений. Делается командой post.
   Можно указать опцию --tags и в параметре перечислить через запятую тэги.
   Пример: post --tags=linux,anime,mplayer ваш ляликс - говно для просмотра аниме!

2. Ответы на сообщения. Делается командой comment.
   Опцией --message указывается сообщение на которое отвечаем. Если отвечаем 
   на комментарий, то указывается в форме "msg.com".
   Примеры: comment --message 123456 ТЫ ГОВНО
            comment --message 123456.123 НЕТ ТЫ

3. Подписка на сообщения, теги и пользователей. Делается командой subscribe (отписка - unsubscribe).
   Чтобы подписаться на тег - указываем --tag=mytag
   Чтобы подписаться на пользователя - указываем --user=somefriend
   Чтобы подписаться на сообщение (комментарии к нему) - указываем --message=messageid
   Список подписок показывается по команде subscriptions.

4. Отображение сообщений. Делается командой show.
   Без аргументов - отображает все последние сообщения (20 штук).
   Каждая следующая опция сокращает вывод:
   Фильтр по тегу: --tag=mytag
   Фильтр по пользователю: --user=somefriend
   Фильтр по номеру сообщения (возвратит одно или ноль): --message=messageid
   
   При использовании фильтра по номеру можно указать --replies, тогда сообщение покажется со всеми комментариями.

5. Короткие и длинные команды и аргументы. Каждая команда имеет укороченное имя:
   post -> p, show -> s, subscribe -> sub, unsubscribe -> usub, subscriptions -> lsub, comment -> c.
   Каждая опция тоже имеет короткое имя, обычно совпадающее с первой буквой длинного.
   Так вместо --tags=tag1,tag2,tag3 можно писать -t tag1,tag2,tag3.
   т.е. если сокращать всё, можно писать так:
      p -t linux,anime,mplayer ваш ляликс - говно для просмотра аниме!
      c -m 123456.123 НЕТ ТЫ

6. Подобие справки. Есть команда help, которая выведет все команды + описание их аргументов, коротких и длинных.

7. Ах, да, самое главное: если весь предыдущий текст вызывает у вас рвоту и мысли "ГОСПОДИ, КУДА Я ПОПАЛ?", 
   то возможно вам понравится интерфейс имитирующий juick. Включить его можно командой:
     interface simplified

"""
    helptext_simple="""

*tagname Blah-blah-blah - Post a message with tag 'tagname'
#1234 Blah-blah-blah - Answer to message #1234
#1234/5 Blah - Answer to reply #1234/5

# - Show last messages from public timeline
#1234 - Show message
#1234+ - Show message with replies
@username - Show user's info and last 20 messages
@username+ - Show user's info and last 20 messages
*tag - Show last 20 messages with this tag
S - Show your subscriptions
S #123 - Subscribe to message replies
S @username - Subscribe to user's blog
S *tag - Subscribe to tag
U #123 - Unsubscribe from comments
U @username - Unsubscribe from user's blog
U *tag - Unsubscribe from tag
PING - Pong :)
INTERFACE redeye - return to redeyed interface"""

    def formatCommand(self,command):
        defer.returnValue(command+':\n'+'\n'.join( (("-"+arg[0]).rjust(4)+(' ARG' if arg[2] else '    ') + \
          ("--"+arg[1]).rjust(10)+('=ARG' if arg[2] else '    ') + \
          ' '+arg[3]) for arg in self.parser.commands[command]))

    @defer.inlineCallbacks
    def handleSimplified(self,command,msg,parameters):
        defer.returnValue('Help:'+self.helptext_simple)

    @defer.inlineCallbacks
    def handleRedeye(self,options,rest,msg):
        defer.returnValue('Help:'+self.helptext)
        #+'\n'.join(self.formatCommand(command) for command in self.parser.commands)
    handleRedeye.arguments = ()

cmd = HelpCommand()
