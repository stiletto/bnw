# -*- coding: utf-8 -*-
# from twisted.words.xish import domish

from base import *
import random

answers = ('Pong, чо.',
           'Pong, хуле.',
           'Pong, блин, pong.',
           'Pong. А что я по-твоему должен был ответить?',
           'Pong です！',
           'Pong. А ты с какова раёна будешь?',
           'Pong. А ты знаешь об опции -s / --safe?')


@require_auth
def cmd_ping(request, safe=None):
    """ Пинг """
    return dict(ok=True, desc='Pong.' if safe else random.choice(answers))


def cmd_fuckoff(request, *args, **kwargs):
    return dict(ok=False, desc='Fuck off. Not implemented')
