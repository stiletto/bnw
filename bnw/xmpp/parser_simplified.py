# -*- coding: utf-8 -*-
import sys
import traceback
import re
import datetime

from base import CommandParserException, BaseParser
from bnw.core.base import BnwResponse
from twisted.internet import defer


def requireAuthSimplified(fun):
    def newfun(self, command, msg, parameters):
        if msg.user is None:
            raise BnwResponse('Only for registered users')
        else:
            return fun(self, command, msg, parameters)
    return newfun


class SimplifiedParser(BaseParser):
    SHOW_RE = re.compile(ur'^#([0-9A-Za-z]+)(/[0-9A-Za-z]+)?(\+)?$')
    SHOW_USER_RE = re.compile(ur'^@([0-9A-Za-z_-]+)(\+)?$')
    # TAG_SYMS=u'0-9A-Za-zА-Яа-я_-'
    SHOW_TAG_RE = re.compile(ur'^\*(\S+)(\+)?$')
    REPLY_RE = re.compile(ur'\A#([0-9A-Za-z]+)(/[0-9A-Za-z]+)? (.+)\Z',
                          re.MULTILINE | re.DOTALL)
    POST_RE = re.compile(
        ur'\A(?:([\*!]\S+)?(?: ([\*!]\S+))?(?: ([\*!]\S+))?(?: ([\*!]\S+))?(?: ([\*!]\S+))? )?(.+)\Z',
        re.MULTILINE | re.DOTALL)  # idiot
    RECO_RE = re.compile(ur'^! +#([0-9A-Za-z]+)(?: (.+))?')

    def __init__(self, commands):
        self.commands = commands

    @defer.inlineCallbacks
    def handleCommand(self, msg):
        ress = self.parse(
            msg.body)  # unicode(msg.body).encode('utf-8','ignore'))
        command = ress[0]
        parameters = ress[1:]
        try:
            # return str(parameters)
            defer.returnValue((yield self.commands['simplified', command]['handler'](command, msg, parameters)))
        except BnwResponse, response:
            defer.returnValue(response)

    def parse(self, text):
        if text == '#':
            return ('show', 'last', None)
        showmatch = self.SHOW_RE.match(text)
        if showmatch:
            return ('show', 'post', showmatch.groups())
        replymatch = self.REPLY_RE.match(text)
        if replymatch:
            return ('reply', replymatch.groups())
        recomatch = self.RECO_RE.match(text)
        if recomatch:
            return ('recommend', recomatch.groups())
        showuser = self.SHOW_USER_RE.match(text)
        if showuser:
            return ('show', 'user', showuser.groups())
        showtag = self.SHOW_TAG_RE.match(text)
        if showtag:
            return ('show', 'tag', showtag.groups())
        findspace = text.find(' ')
        if findspace != -1:
            cmd = text[:findspace]
            if cmd.isupper() and (('simplified', cmd) in self.commands):
                return (cmd, text[findspace + 1:])
        elif text.isupper() and (('simplified', text) in self.commands):
            return (text,)
        postmatch = self.POST_RE.match(text)
        if postmatch is None:
            raise CommandParserException(
                'Parser facepalmed. What were you meaning?')
        return ('post', postmatch.groups())
