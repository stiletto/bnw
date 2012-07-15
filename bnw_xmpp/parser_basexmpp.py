# -*- coding: utf-8 -*-

from twisted.internet import defer

import re
import base

class BaseXmppParser(base.BaseParser):
    def formatResult(self,request,result):
        if not isinstance(result,dict):
            return 'ERROR. Parser has got a strange shit from handler.'
        else:
            ok = result.get('ok','WUT')
            if ok=='WUT':
                return 'Result unknown.'
            else:
                fmt = result.get('format',None)
                if fmt:
                    formatter = self.formatters.get(fmt,None)
                    if formatter:
                        return formatter(request,result)
                desc = result.get('desc','')
                if ok:
                    return desc
                else:
                    return 'ERROR. '+desc
