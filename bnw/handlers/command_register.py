# -*- coding: utf-8 -*-
# from twisted.words.xish import domish

from base import *
import random
import time
import bnw.core.bnw_objects as objs


def _(s, user):
    return s

from uuid import uuid4
import re


@check_arg(name=USER_RE)
def cmd_register(request, name=""):
        """ Регистрация """
        if request.user:
            return dict(ok=False,
                     desc=u'You are already registered as %s' % (
                         request.user['name'],),
                     )
        else:
            name = name.lower()[:128]
            if name == 'anonymous':
                return dict(ok=False, desc=u'You aren''t anonymous.')

            user = objs.User({'id': uuid4().hex,
                              'name': name,
                              'login_key': uuid4().hex,
                              'regdate': int(time.time()),
                              'jid': request.jid.userhost(),
                              'interface': 'redeye',
                              'settings': {
                              'servicejid': request.to.userhost()
                              },
                              })
            if not objs.User.find_one({'name': name}):
                user.save()
                return dict(ok=True, desc='We registered you as %s.' % (name,))
            else:
                return dict(ok=True, desc='This username is already taken')
