# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

import formatters_redeye
import formatters_simple

redeye_formatters = {
    'comment': formatters_redeye.formatter_comment,
    'message': formatters_redeye.formatter_message,
    'recommendation': formatters_redeye.formatter_recommendation,
}

simple_formatters = {
    'comment': formatters_simple.formatter_comment,
    'message': formatters_simple.formatter_message,
    'recommendation': formatters_simple.formatter_recommendation,
}

parsers={}
parsers['redeye']=redeye_formatters
parsers['simplified']=simple_formatters

