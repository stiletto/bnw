# coding: utf-8

from twisted.internet import defer

import deliver_formatters
import base
class XmppNotifier(object):
    #@defer.inlineCallbacks
    def notify(self,user,event_type,event):
        if event_type=='message' and not user.get('off',False):
            message,recommender,recocomment,sfrom = event
            if recommender:
                formatter = deliver_formatters.parsers[user.get('interface','redeye')]['recommendation']
            else:
                formatter = deliver_formatters.parsers[user.get('interface','redeye')]['message']
            formatted = formatter(None,
                dict(message=message,
                     recommender=recommender,
                     recocomment=recocomment)
            )
            user.send_plain(formatted,sfrom)
            return 1 #defer.returnValue(1)
        elif event_type=='comment' and not user.get('off',False):
            comment,sfrom = event
            formatter = deliver_formatters.parsers[user.get('interface','redeye')]['comment']
            formatted = formatter(None,
                dict(comment=comment)
            )
            user.send_plain(formatted,sfrom)
            return 1 #defer.returnValue(1)
        return 0 #defer.returnValue(0)
