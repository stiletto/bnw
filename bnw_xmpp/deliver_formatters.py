# -*- coding: utf-8 -*-
#from twisted.words.xish import domish
from base import XmppResponse

import formatters_redeye

redeye_formatters = {
    'comment': formatters_redeye.formatter_comment,
    'message': formatters_redeye.formatter_message,
    'recommendation': formatters_redeye.formatter_recommendation,
}

parsers={}
parsers['redeye']=redeye_formatters
