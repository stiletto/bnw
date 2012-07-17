# -*- coding: utf-8 -*-

from twisted.internet import defer

import re
import base

class BaseXmppParser(base.BaseParser):
    def formatResult(self, request, result):
        if not isinstance(result, dict):
            return 'ERROR. Parser has got a strange shit from handler.'

        ok = result.get('ok')
        if ok is None:
            return 'Result unknown.'
        else:
            fmt = result.get('format')
            if fmt:
                formatter = self.formatters.get(fmt)
                if formatter:
                    return formatter(request, result)
            desc = result.get('desc', '')
            if ok:
                return 'OK. ' + desc
            else:
                return 'ERROR. ' + desc
