# -*- coding: utf-8 -*-

from base import CommandParserException
from bnw.core.base import BnwResponse
from twisted.internet import defer
import parser_basexmpp

import alias_subst


class RedEyeParser(parser_basexmpp.BaseXmppParser):
    def __init__(self, commands, aliases, formatters):

        self.commands = {}
        self._commands = {}
        self.commandfuns = {}
        self.helpmsgs = {}
        self.formatters = formatters

        for cmd in commands:
            assert len(cmd) in (3, 4)
            if len(cmd) == 4:
                name, args, handler, restname = cmd
            else:
                name, args, handler = cmd
                restname = None
            args+=(('h','help',False,u'Show list of possible arguments'),)

            alias = aliases.get(name)

            self.commands[name] = args
            self.commands[alias] = args

            self.commandfuns[name] = handler, restname
            self.commandfuns[alias] = handler, restname

            helpmsg = self.generate_help_message(name, alias)
            self.helpmsgs[name] = helpmsg
            self.helpmsgs[alias] = helpmsg

    def hashCommand(self, cmd):
        self._commands[cmd] = {"short": {}, "long": {}}
        args = self.commands[cmd]
        for arg in args:
            if arg[0]:
                self._commands[cmd]['short'][arg[0]] = arg
            if arg[1]:
                self._commands[cmd]['long'][arg[1]] = arg

    def getHashed(self, cmd):
        if not cmd in self._commands:
            self.hashCommand(cmd)
        return self._commands[cmd]

    def parseArgument(self, argi, prevopt, arg):
            # print "PA",prevopt,arg
        if prevopt:
            return None, ((prevopt, arg),), False
        elif arg == '--':
            return None, (), True
        elif arg.startswith('--'):
            namevalue = arg[2:].split('=')
            name = namevalue[0]
            if not name in argi['long']:
                raise CommandParserException('Unknown option %s' % name)
            if argi['long'][name][2]:  # option requires an argument
                if len(namevalue) < 2:
                    raise CommandParserException(
                        'Option %s requires an argument' % name)
                value = namevalue[1]
            else:
                value = True
            return False, ((name, value),), False
        elif arg.startswith('-'):
            shorts = []
            for j, c in enumerate(arg[1:]):
                if prevopt:
                    shorts.append((prevopt, arg[j + 1:]))
                    prevopt = None
                    break
                if not c in argi['short']:
                    raise CommandParserException('Unknown short option %s' % c)
                if not argi['short'][c][2]:
                    shorts.append((argi['short'][c][1], True))
                else:
                    prevopt = argi['short'][c][1]
            return prevopt, shorts, False

    def generate_help_message(self, cmd, alias):
        # Example entry of self.commands:
        # ("u", "user", True, u"Blacklist user."),

        # Result is going to look like that:
        # -a        --aoption        Description for a
        # -b ARG    --boption=ARG    Description for b

        # We collect data into three lists (representing columns):
        shortopts = []
        shortopts_colwidth = 0
        longopts = []
        longopts_colwidth = 0
        descriptions = []
        desc_colwidth = 0

        # put options and descriptions into appropriate columns
        for shortname, longname, arg_required, helpmsg in self.commands[cmd]:
            shortopt = ""
            if shortname:
                shortopt = "-" + shortname
                if arg_required:
                    shortopt += " ARG"

            longopt = ""
            if longname:
                longopt = "--" + longname
                if arg_required:
                    longopt += "=ARG"

            shortopts.append(shortopt)
            longopts.append(longopt)
            descriptions.append(helpmsg)

            shortopts_colwidth = max(shortopts_colwidth, len(shortopt))
            longopts_colwidth = max(longopts_colwidth, len(longopt))
        # pad list elements to match column width
        shortopts = self.pad_to_colwidth(shortopts, shortopts_colwidth)
        longopts = self.pad_to_colwidth(longopts, longopts_colwidth)

        # self.commandfuns contains the name of the positional argument that
        # the command accepts. Let's look it up!
        _, restname = self.commandfuns[cmd]
        options_usage = (" " + restname if restname else "")
        result = u"Usage: %s" % cmd + options_usage
        if alias:
            result += u"\n       %s" % alias + options_usage

        # join columns linewise
        line_tuples = zip(shortopts, longopts, descriptions)
        join = lambda acc, x: acc + '\n' + "    ".join(x)
        lines = reduce(join, line_tuples, result);

        return lines

    def formatCommandHelp(self, cmd):
        return self.helpmsgs[cmd]

    """
    Pads each string in a list to match required width
    """
    def pad_to_colwidth(self, lst, width):
        return map(lambda x: x + (" " * (width - len(x))), lst)

    def alias_resolve(self, msg):
        if msg.user:
            text = msg.body
            cmda = text.split(' ', 1)
            alias = msg.user.get('aliases', {}).get(cmda[0], None)
            if alias:
                if len(cmda) < 2:
                    cmda.append('')
                msg.body = alias_subst.arg_substitution(alias, cmda[1].strip())
                return self.resolve(msg)
        return None, None, None, None, None

    @defer.inlineCallbacks
    def handle(self, msg):
        cmdname, handler, restname, options, rest = self.resolve(
            msg)  # unicode(msg.body).encode('utf-8','ignore'))
        if not handler:
            cmdname, handler, restname2, options, rest = self.alias_resolve(msg)
            if not handler:
                defer.returnValue('ERROR. Command not found: %s' % (restname,))
            else:
                restname = restname2
        try:
            if 'help' in options:
                defer.returnValue((yield
                    self.formatCommandHelp(cmdname.lower())))
            if restname:
                options[restname] = rest
            options = dict((str(k), v) for k, v in options.iteritems(
            ))  # deunicodify options keys
            result = yield handler(msg, **options)
            defer.returnValue(self.formatResult(msg, result))
        except BnwResponse, response:
            defer.returnValue(response)

    def resolve(self, msg):
        text = msg.body
        inquotes = None
        firstsym = True
        wordbegin = -1
        prevopt = None
        rest = u''
        waitcommand = True
        options = {}
        wordbuf = []
        cmdname = u''
            # i know it's ugly and slow. is there any better way to implement
            # quotes?
        for i, c in enumerate(text):
            if (c == ' ' and not inquotes) or c == '\n':
                inquotes = None
                if len(wordbuf) > 0:  # 1: \todo check why there was 1
                    if waitcommand:
                        waitcommand = False
                        cmdname = ''.join(wordbuf).lower()  # text[wordbegin:i]
                        handler_tuple = self.commandfuns.get(cmdname, None)
                        if not handler_tuple:
                            # raise CommandParserException('No such command:
                            # "%s"' % cmdname)
                            return None, None, cmdname, None, None
                        argi = self.getHashed(cmdname)
                    else:
                        prevopt, newopts, stop = self.parseArgument(
                            argi, prevopt, ''.join(wordbuf))
                        for name, value in newopts:
                            options[name] = value
                        if stop:
                            rest = text[i+1:]
                            break
                wordbuf = []
                firstsym = True
            elif c in ('"', "'"):
                if not inquotes:
                    inquotes = c
                elif inquotes == c:
                    inquotes = None
                else:
                    wordbuf.append(c)
            else:
                if firstsym:
                    wordbegin = i
                    firstsym = False
                    if c != '-' and not (prevopt or waitcommand):
                        if inquotes:
                            rest = inquotes + text[i:]
                        else:
                            rest = text[i:]
                        break
                wordbuf.append(c)
        else:
            if inquotes:
                raise CommandParserException(
                    "Ouch! You forgot to close quotes <%s> " % inquotes)
            if waitcommand:
                cmdname = ''.join(wordbuf).lower()
                handler_tuple = self.commandfuns.get(cmdname, None)
                if not handler_tuple:
                    raise CommandParserException(
                        'No such command: %s' % cmdname)
            elif len(wordbuf) > 0:
                prevopt, newopts, stop = self.parseArgument(
                    argi, prevopt, ''.join(wordbuf))
                if prevopt:
                    raise CommandParserException(
                        "Option %s requires an argument" % argi['long'][prevopt][0])
                for name, value in newopts:
                    options[name] = value
        handler, restname = handler_tuple
        return (cmdname, handler, restname, options, rest)
