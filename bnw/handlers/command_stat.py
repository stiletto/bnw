# -*- coding: utf-8 -*-

import time
from base import *
import bnw.core.bnw_objects as objs


def cmd_stat(request):
    messages = list(x.doc for x in objs.StatMessages.find({},limit=100000))
    comments = list(x.doc for x in objs.StatComments.find({},limit=100000))
    return dict(ok=True, desc='Oh, hai!', messages=messages,
                      comments=comments, cache=3600, cache_public=True)
