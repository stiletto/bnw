# -*- coding: utf-8 -*-

from base import *
from twisted.internet import defer
import bnw_core.bnw_objects as objs
from uuid import uuid4


@require_auth
#@check_arg(jid=USER_RE)
@defer.inlineCallbacks
def cmd_jids(request, add="", delete="", select=""):
    """ Переключение JID'ов
    
    Добавление, удаление, выбор активного JID.
    simple: JID +example@example.com -- Добавить JID, JID -example@example.com, JID  """
    #user=user.lower()
    if not ('jids' in request.user):
        request.user['jids'] = [ request.user['jid'] ]
        request.user['pending_jids'] = []
    if add:
        if (add in request.user['jids']) or (add in request.user['pending_jids']):
            defer.returnValue(dict(ok=False, desc='JID already added.'))
        other_user=yield objs.User.find_one({'jids': add})
        if not other_user:
            other_user=yield objs.User.find_one({'pending_jids': add})
        if not other_user:
            other_user=yield objs.User.find_one({'jid': add})
        if other_user:
            defer.returnValue(dict(ok=False, desc='JID is being used by other user.'))
        if len(request.user['jids'])>16:
            defer.returnValue(dict(ok=False, desc='Why would you need SO MANY JIDs?'))
        if len(request.user['pending_jids'])>5:
            defer.returnValue(dict(ok=False, desc='Too many pending JIDs aargh.'))

        request.user['pending_jids'].append(add)
        _ = yield request.user.save()
        defer.returnValue(dict(ok=True, desc='Please send "confirm %s" from JID being added to confirm JID ownership.' % (request.user['name'], )))
    if delete:
        if delete in request.user['jids']:
            if delete==request.user['jid']:
                defer.returnValue(dict(ok=False, desc='Cannot delete active jid.'))
            request.user['jids'].remove(delete)
            request.user['jid'] = request.user['jids'][0]
            _ = yield request.user.save()
            defer.returnValue(dict(ok=True, desc='JID deleted.'))
        elif delete in request.user['pending_jids']:
            request.user['pending_jids'].remove(delete)
            _ = yield request.user.save()
            defer.returnValue(dict(ok=True, desc='Unconfirmed JID deleted.'))
        else:
            defer.returnValue(dict(ok=False, desc='No such JID.'))
    if select:
        if select == 'this':
            select = request.jid.userhost()
        if select in request.user['jids']:
            request.user['jid']=select
            _ = yield request.user.save()
            defer.returnValue(dict(ok=True, desc='Active JID changed.'))
        else:
            defer.returnValue(dict(ok=False, desc='No such JID.'))
    if not (add or delete or select):
        defer.returnValue(dict(ok=True, desc='List of jids',
            jid=request.user['jid'], jids=request.user['jids'],
            pending_jids=request.user['pending_jids'],
            format='jids'))


@defer.inlineCallbacks
def cmd_confirm(request, code):
    """ Подтверждение JID'а """
    if request.user:
        defer.returnValue(dict(ok=False, desc='You are already registered.'))

    teh_user=yield objs.User.find_one({'pending_jids': request.jid.userhost(), 'name': code})
    if not teh_user:
        defer.returnValue(dict(ok=False, desc='This JID wasn''t added for this user.'))
    teh_user['pending_jids'].remove(request.jid.userhost())
    teh_user['jids'].append(request.jid.userhost())
    _ = yield teh_user.save()
    defer.returnValue(dict(ok=True, desc='JID added.'))
