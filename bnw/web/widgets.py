# -*- coding: utf-8 -*-

import time
import datetime
import tornado.escape


class Widgets(object):
    """Common user interface rendering helpers."""

    def runums(self, n, d1, d2, d5):
        """Return russian numeral according to given number and
        basic numerals.
        """
        n = n % 100
        if 10 < n < 15:
            return d5
        n = n % 10
        if n == 1:
            return d1
        elif 1 < n < 5:
            return d2
        else:
            return d5

    def tag(self, tag, user=None):
        pars = {
            'tu': tornado.escape.url_escape(tag, plus=False),
            't': tornado.escape.xhtml_escape(tag[:32]),
            'u': user,
        }
        if user:
            return '<a href="/u/%(u)s/t/%(tu)s" class="tag">%(t)s</a>' % pars
        else:
            return '<a href="/t/%(tu)s" class="tag">%(t)s</a>' % pars

    def club(self, club, user=None):
        pars = {
            'tu': tornado.escape.url_escape(club, plus=False),
            't': tornado.escape.xhtml_escape(club[:32]),
            'u': user
        }
        return '<a href="/c/%(tu)s" class="club">%(t)s</a>' % pars

    def tags(self, tags, clubs, user=None):
        return ('<div class="tags">' +
                ' '.join(self.club(c, user) for c in clubs) + ' ' +
                ' '.join(self.tag(t, user) for t in tags) + ' </div>')

    def user_url(self, name):
        return '/u/%(u)s' % {'u': name}

    def post_url(self, name):
        return '/p/%(u)s' % {'u': name}

    def userl(self, name):
        return '<a href="/u/%(u)s" class="usrid">@%(u)s</a>' % {'u': name}

    def msgl(self, msg, bookmark=False):
        bm = ' rel="bookmark"' if bookmark else ''
        return '<a href="/p/%(u)s"%(bm)s class="msgid">#%(n)s</a>' % {
            'u': msg.replace('/', '#'),
            'n': msg,
            'bm': bm,
        }

    def time(self, timestamp):
        dn = datetime.datetime.utcnow()
        dt = datetime.datetime.utcfromtimestamp(timestamp)
        dd = dn - dt
        res = ''
        if dd.days > 0:
            res = (str(dd.days) + ' ' +
                   self.runums(dd.days, u'день', u'дня', u'дней'))
        else:
            if dd.seconds > 3600:
                hours = dd.seconds / 3600
                res = (str(hours) + ' ' +
                       self.runums(hours, u'час', u'часа', u'часов'))
            elif dd.seconds > 60:
                minutes = dd.seconds / 60
                res = (str(minutes) + ' ' +
                       self.runums(minutes, u'минуту', u'минуты', u'минут'))
            else:
                res = (str(dd.seconds) + ' ' +
                       self.runums(dd.seconds, u'секунду', u'секунды', u'секунд'))
        return ('<abbr class="published" ' +
                'title="' + dt.strftime('%Y-%m-%dT%H:%M:%S+0000') + '">' +
                res + u' назад</abbr>')

    def messages(self, count):
        return self.runums(count, u'сообщение', u'сообщения', u'сообщений')

    def comments(self, count):
        return self.runums(count, u'комментарий', u'комментария', u'комментариев')

    def shorttext(self, txt, maxwords=7, maxlen=70, ellipsis=u'…'):
        words = 0
        pos = 0
        lt = len(txt)
        while words < maxwords and pos < lt:
            prevpos = pos
            pos = txt.find(' ', pos + 1)
            if pos == -1:
                pos = lt
            if pos >= maxlen:
                if ellipsis and pos < lt:
                    return txt[:prevpos] + ellipsis
                else:
                    return txt[:prevpos]
            words += 1
        if ellipsis and pos < lt:
            return txt[:pos] + ellipsis
        else:
            return txt[:pos]

    def ranq(self):
        phrases = (
            u'↑↑↓↓←→←→ⒷⒶ',
            u'Где блекджек, где мои шлюхи? Ничерта не работает!',
            u'Бляди тоже ок, ага.',
            u'Шлюхи без блекджека, блекджек без шлюх.',
            u'Бабушка, смотри, я сделал двач!',
            u'БЕГЕМОТИКОВ МОЖНО!',
            u'ビリャチピスデツナフイ',
            u'Best viewed with LeechCraft on Microsoft Linux.',
            u'Я и мой ёбаный кот на фоне ковра.',
            u'УМННБJ, ЯХВ.',
            u'Два года в /fg/.',
            u'Тут не исправить уже ничего, Господь, жги!',
            # Шрифты говно.
            (u'\u0428\u0300\u0310\u0314\u0301\u033e\u0303\u0352\u0308\u0314'
             u'\u030e\u0334\u035c\u0334\u0341\u0341\u031c\u0325\u034d\u0355'
             u'\u033c\u0319\u0331\u0359\u034e\u034d\u0318\u0440\u0367\u0364'
             u'\u034b\u0305\u033d\u0367\u0308\u0310\u033d\u0306\u0310\u034b'
             u'\u0364\u0366\u036c\u035b\u0303\u0311\u035e\u0327\u031b\u035e'
             u'\u033a\u0356\u0356\u032f\u0316\u0438\u0312\u0365\u0364\u036f'
             u'\u0342\u0363\u0310\u0309\u0311\u036b\u0309\u0311\u0489\u031b'
             u'\u034f\u0338\u033b\u0355\u0347\u035a\u0324\u0355\u0345\u032f'
             u'\u0331\u0333\u0349\u0444\u0314\u0343\u0301\u031a\u030d\u0357'
             u'\u0362\u0321\u035e\u0334\u0334\u031f\u031e\u0359\u0319\u033b'
             u'\u034d\u0326\u0345\u0354\u0324\u031e\u0442\u0310\u036b\u0302'
             u'\u034a\u0304\u0303\u0365\u036a\u0328\u034f\u035c\u035c\u032b'
             u'\u033a\u034d\u031e\u033c\u0348\u0329\u0325\u031c\u0354\u044b'
             u'\u0305\u0351\u034c\u0352\u036b\u0352\u0300\u0365\u0350\u0364'
             u'\u0305\u0358\u0315\u0338\u0334\u0331\u033a\u033c\u0320\u0326'
             u'\u034d\u034d\u034d\u0331\u0316\u0354\u0316\u0331\u0349.\u0366'
             u'\u0306\u0300\u0311\u030c\u036e\u0367\u0363\u036f\u0314\u0302'
             u'\u035f\u0321\u0335\u0341\u0334\u032d\u033c\u032e\u0356\u0348'
             u'\u0319\u0356\u0356\u0332\u032e\u032c\u034d\u0359\u033c\u032f'
             u'\u0326\u032e\u032e\u0433\u034c\u036e\u030f\u0308\u0342\u036f'
             u'\u031a\u0489\u0340\u0358\u031b\u035e\u0319\u032c\u0318\u0332'
             u'\u0317\u0347\u0355\u0320\u0319\u0345\u0359\u033c\u0329\u035a'
             u'\u043e\u0313\u0364\u033d\u0352\u030b\u0309\u0300\u0302\u0304'
             u'\u0312\u0343\u030a\u0368\u035b\u0301\u030c\u0364\u0302\u0337'
             u'\u0340\u0360\u0325\u032f\u0318\u0432\u0312\u0352\u0343\u030f'
             u'\u031a\u0313\u0336\u0489\u031b\u035c\u0319\u0318\u033a\u0330'
             u'\u032e\u033c\u031f\u033c\u0325\u031f\u0318\u0320\u031c\u043d'
             u'\u033f\u0314\u0303\u0368\u0351\u0338\u0337\u0338\u0332\u031d'
             u'\u0348\u0359\u0330\u031f\u033b\u031f\u0330\u031c\u031f\u0317'
             u'\u034e\u033b\u033b\u034d\u043e\u0314\u0300\u030b\u036b\u0307'
             u'\u033f\u0310\u036b\u034c\u0357\u0369\u0489\u0315\u0328\u0361'
             u'\u035c\u031c\u0319\u0319\u0348\u034d\u032e\u032e\u033c\u0319'
             u'\u0318\u031e'),
        )
        return phrases[int(time.time()) / 10 % len(phrases)]


widgets = Widgets()
