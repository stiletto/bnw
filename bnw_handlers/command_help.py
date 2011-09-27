# -*- coding: utf-8 -*-
#from twisted.words.xish import domish
from twisted.web.client import getPage

from base import *
import random

helptext="""
1. Постинг сообщений. Делается командой post.
   Можно указать опцию --tags и в параметре перечислить через запятую тэги.
   Пример: post --tags=linux,anime,mplayer ваш ляликс - говно для просмотра аниме!

2. Ответы на сообщения. Делается командой comment.
   Опцией --message указывается сообщение на которое отвечаем. Если отвечаем 
   на комментарий, то указывается в форме "msg/com".
   Примеры: comment --message=123456 ТЫ ГОВНО
            comment --message=123456/123 НЕТ ТЫ

3. Само собой, как нагадил, так можно и убрать. Команда delete (d) удаляет посты и
   комментарии. Посты можно удалять только свои, комментарии свои + чужие в своих тредах.
   Примеры: delete --message=123456
            delete --message=123456/789
            d -m ABCDEF
            d -m ABCDEF/XYZ

4. Подписка на сообщения, теги и пользователей. Делается командой subscribe (отписка - unsubscribe).
   Чтобы подписаться на тег - указываем --tag=mytag
   Чтобы подписаться на пользователя - указываем --user=somefriend
   Чтобы подписаться на сообщение (комментарии к нему) - указываем --message=messageid
   Список подписок показывается по команде subscriptions.

5. Отображение сообщений. Делается командой show.
   Без аргументов - отображает все последние сообщения (20 штук).
   Каждая следующая опция сокращает вывод:
   Фильтр по тегу: --tag=mytag
   Фильтр по пользователю: --user=somefriend
   Фильтр по номеру сообщения (возвратит одно или ноль): --message=messageid
   
   При использовании фильтра по номеру можно указать --replies, тогда сообщение покажется со всеми комментариями.

6. Короткие и длинные команды и аргументы. Каждая команда имеет укороченное имя:
   post -> p, show -> s, subscribe -> sub, unsubscribe -> usub, subscriptions -> lsub, comment -> c.
   Каждая опция тоже имеет короткое имя, обычно совпадающее с первой буквой длинного.
   Так вместо --tags=tag1,tag2,tag3 можно писать -t tag1,tag2,tag3.
   т.е. если сокращать всё, можно писать так:
      p -t linux,anime,mplayer ваш ляликс - говно для просмотра аниме!
      c -m 123456/123 НЕТ ТЫ

7. Подобие справки. Есть команда help, которую вы читаете,
   а еще у каждой команды есть опция --help которая выведет описание аргументов, коротких и длинных.

8. Ах, да, самое главное: если весь предыдущий текст вызывает у вас рвоту и мысли "ГОСПОДИ, КУДА Я ПОПАЛ?", 
   то возможно вам понравится интерфейс имитирующий juick. Включить его можно командой:
     interface simplified

"""
helptext_simple="""
!club *tag blah-blah-blah - отправить сообщение с тэгом “tag” в клуб “club”
#number blah-blah-blah - отправить комментарий к сообщению #number
#number/id blah-blah-blah - ответить на комментарий #number/id
! #number Look at this idiot! - рекомендовать сообщение с заметкой (можно и без неё)
PM @user - отправить личное сообщение пользователю @user

D - удалить: сообщение - D #number, комментарий - D #number/id, последнее сообщение - D L

# - показать последние сообщения
!club - показать последние сообщения клуба “club”
*tag - показать последнее сообщения с тэгом “tag”
#number - показать сообщение (без ответов)
#number+ - показать сообщение (с ответами)
#number/id - показать комментарий #number/id

S - показать список подписок или подписаться: пользователь - S @user, тэг - S *tag, клуб - S !club, сообщение - S #number
U - отписаться от: пользователя - U @user, тэга - U *tag, клуба - U !club, сообщения - U #number
BL - показать чёрный список
BL + - добавить в чёрный список: пользователя - BL +@user, тэг - BL +*tag, клуб - BL +!club
BL - - удалить из чёрного списка: пользователя - BL -@user, тэг - BL -*tag, клуб - BL -!club

? string - искать сообщения, которые содержат текст "string"

PING (ПИНГ, ЗШТП) - Пинг
INTERFACE - выбор интерфейса (redeye - консолеподобный, simplified - жуйкоподобный)
VCARD - обновить VCARD
USERLIST [page] - список всх пользователей, 50 на страницу
LOGIN - получить ссылку для входа на сайт."""
def de_yo(s):
    return s.replace('ё','е')+'\n\n@l29ah - лох :3'

HELP_BASE='http://hive.blasux.ru/u/Stiletto/bnw/help/'
def formatCommand(command):
        defer.returnValue(command+':\n'+'\n'.join( (("-"+arg[0]).rjust(4)+(' ARG' if arg[2] else '    ') + \
          ("--"+arg[1]).rjust(10)+('=ARG' if arg[2] else '    ') + \
          ' '+arg[3]) for arg in elf.parser.commands[command]))

@defer.inlineCallbacks
def cmd_help_simple(request):
    """ Справка """
    page = yield getPage(HELP_BASE+'simplified'+'?action=raw')
    if page.startswith('{{{\r\n'): page=page[3:]
    if page.endswith('}}}\r\n'): page=page[:-5]
    defer.returnValue(
        dict(ok=True,desc='Help:'+(page if random.random()<0.9 else de_yo(page)) + \
            ('\n\nАлсо, @vrusha - няша' if random.random() > 0.65 else ''),cache=3600,cache_public=True))

def cmd_help_redeye(request):
    """ Справка """
    return dict(ok=True,desc='Help:'+helptext,cache=3600,cache_public=True)
        #+'\n'.join(self.formatCommand(command) for command in self.parser.commands)
