# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

from base import *
import random
import bnw_core.bnw_objects as objs

def _(s,user):
    return s
from uuid import uuid4
import re


@check_arg(name=USER_RE)
@defer.inlineCallbacks
def cmd_register(request,name=""):
        if request.user:
            defer.returnValue(
                dict(ok=False,
                     desc=_(u'You are already registered as %s',request) % (request.user['name'],)
                )
            )
        else:
            name=name.lower()
            if name=='anonymous':
                defer.returnValue(
                    dict(ok=False,desc=u'You aren''t anonymous.')
                )

            user=objs.User({ 'id': uuid4().hex,
                   'name': name,
                   'login_key': uuid4().hex,
                   'regdate': int(time.time()),
                   'jid': request.bare_jid,
                   'interface': 'redeye',
                 })
            if not (yield objs.User.find_one({'name':name})):
                _ = yield user.save()
                defer.returnValue(
                    dict(ok=True,desc='We registered you as %s.' % (name,))
                )
            else:
                defer.returnValue(
                    dict(ok=True,desc='This username is already taken')
                )
