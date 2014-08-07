# -*- coding: utf-8 -*-
# from twisted.words.xish import domish
from twisted.web.client import getPage

from base import *
import random

helptext = """
Здесь приведён лишь перечень команд и общие сведения. Чтобы узнать больше
о конкретной команде, используйте опцию --help, например:

    post --help

Доступные команды:
    help        Справка (её-то вы как раз и читаете)
    ping        Пингануть BNW
    register    Регистрация ника
    search      Поиск по постам и комментариям
    interface   Смена типа интерфейса (сейчас вы читаете справку по «redeye»)
    subscribe, unsubscribe, subscriptions
                Управление подписками на пользователей, клубы и комментарии
    feed        Показать ленту
    today       Показать обсуждаемое за последние 24 часа
    show        Показать сообщение или пользователя
    post        Запостить сообщение
    comment     Комментировать сообщение
    recommend   Рекомендовать сообщение
    delete      Удалить сообщение или комментарий
    bl          Управление блеклистом
    pm          Отправить пользователю приватное сообщение
    on, off     Включить/выключить доставку новых сообщений и комментариев
    login       Получить URL, по которому можно зайти в веб-интерфейс
    vcard       Заставить BNW запросить ваш VCard
    userlist    Показать список пользователей
    clubs       Показать список клубов
    update      Поправить теги/клубы сообщения
    set         Управление опциями
    jids        Переключение JID'ов
    confirm     Подтверждение JID'а
    alias       Управление алиасами

Ах, да, самое главное: если весь предыдущий текст вызывает у вас рвоту и мысли
"ГОСПОДИ, КУДА Я ПОПАЛ?", то, возможно, вам больше понравится интерфейс,
имитирующий Juick. Включить его можно командой:

    interface simplified
"""
helptext_simple = """
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
    return s.replace('ё', 'е') + '\n\n@l29ah - лох :3'

HELP_BASE = 'http://hive.blasux.ru/u/Stiletto/BnW/help_'


def formatCommand(command):
        defer.returnValue(command + ':\n' + '\n'.join((("-" + arg[0]).rjust(4) + (' ARG' if arg[2] else '    ') +
                         ("--" + arg[1]).rjust(10) + ('=ARG' if arg[2] else '    ') +
            ' ' + arg[3]) for arg in elf.parser.commands[command]))


@defer.inlineCallbacks
def cmd_help_simple(request):
    """ Справка """
    page = yield getPage(HELP_BASE + 'simplified' + '?action=raw')
    if page.startswith('{{{\r\n'):
        page = page[3:]
    if page.endswith('}}}\r\n'):
        page = page[:-5]
    defer.returnValue(
        dict(ok=True, desc='Help:' + (page if random.random() < 0.9 else de_yo(page)) +
            ('\n\nАлсо, @vrusha - няша' if random.random() > 0.65 else ''), cache=3600, cache_public=True))


def cmd_help_redeye(request):
    """ Справка """
    return dict(ok=True, desc='Help:' + helptext, cache=3600, cache_public=True)
        #+'\n'.join(self.formatCommand(command) for command in self.parser.commands)
