# -*- coding: utf-8 -*-
# from twisted.words.xish import domish

from base import *
import random

import bnw.core.bnw_objects as objs


def bl_internal(user, what, delete, text):
    action = '$pull' if delete else '$addToSet'
    return objs.User.mupdate({'name': user}, {action: {'blacklist': [what, text]}})


@require_auth
def cmd_blacklist(request, user="", tag="", club="", delete=""):
    """ Черный список """
    if not delete and len(request.user.get('blacklist', [])) > 2048:
        return dict(ok=False, desc='Stop being a blacklist-faggot.')

    if (user and tag) or (user and club) or (tag and club):
        return dict(ok=False, desc='Complex subscriptions and blacklist aren''t supported.')

    if user:
        bl_internal(request.user['name'], 'user', delete, user[:128])
    elif tag:
        bl_internal(request.user['name'], 'tag', delete, tag[:256])
    elif club:
        bl_internal(request.user['name'], 'club', delete, club[:256])
    else:
        return dict(ok=True, format="blacklist",
                    blacklist=request.user.get('blacklist', []))
    return dict(ok=True, desc='Blacklist updated.')
