# -*- coding: utf-8 -*-
import sys
import traceback
import datetime

from base import XmppResponse, CommandParserException, BaseParser
from twisted.internet import defer

def requireAuthRedeye(fun):
    def newfun(self,options,rest,msg):
        if msg.user is None:
            raise XmppResponse('Only for registered users')
        else:
            return fun(self,options,rest,msg)
    return newfun


def formatMessage(msg):
    result='+++ [%s] %s:\n' % (
        datetime.datetime.utcfromtimestamp(msg['date']).strftime('%d.%m.%Y %H:%M:%S'),
        msg['user'],)
    if msg['tags']:
        result+='Tags: %s\n' % (', '.join(msg['tags']),)
    if msg['clubs']:
        result+='Clubs: %s\n' % (', '.join(msg['clubs']),)
    result+='\n%s\n' % (msg['text'],)
    result+='--- %(id)s (%(rc)d) http://bnw.blasux.ru/p/%(id)s' % { 
              'id': msg['id'].upper(),
              'rc':    msg['replycount'],
            }
    return result

def formatComment(msg,short=False):
    args={ 'id':    msg['id'].split('/')[1].upper(),
              'author':msg['user'],
              'message':msg['message'].upper(),
              'replyto':None if msg['replyto'] is None else msg['replyto'].upper(),
              'replytotext': msg['replytotext'],
              'text':  msg['text'],
              'num':   msg.get('num',-1),
              'date':  datetime.datetime.utcfromtimestamp(msg['date']).strftime('%d.%m.%Y %H:%M:%S')
         }
    formatstring='+++ [ %(date)s ] %(author)s'
    if msg['replyto']:
        formatstring+=' (in reply to %(replyto)s):\n'
    else:
        formatstring+=' (in reply to %(message)s):\n'
    if not short:
        formatstring+='>%(replytotext)s\n'
    formatstring+='\n%(text)s\n--- %(message)s/%(id)s (%(num)d) http://bnw.blasux.ru/p/%(message)s#%(id)s'
    return formatstring % args

class RedEyeParser(BaseParser):
    def __init__(self,commands):
        #self.commands = { "ls": (
        #        ("a", "all", False, u"List all shits"),
        #        ("h", "human", False, u"Human-readable shits"),
        #        ("n", "number", True, u"Number of shits"),
        #    ),
        #}
        self.commands = commands
        self._commands = {}
        self.commandfuns= {}
        #self.generatelists()
    
    def registerCommand(self,name,arguments,cmdfun):
        self.commands[name]=arguments
        self.commandfuns[name]=cmdfun
        self._commands[name] = { "short": {}, "long": {} }
        for arg in arguments:
            if arg[0]:
                self._commands[name]['short'][arg[0]]=arg
            if arg[1]:
                self._commands[name]['long'][arg[1]]=arg
        self.generatelists()
    
    def hashCommand(self,cmd):
        self._commands[cmd]={ "short": {}, "long": {} }
        args=self.commands['redeye',cmd]
        args=args['handler'].arguments+(('h','help',False,'Show list of possible arguments (autogenerated)'),)
        #self.commandfuns[cmd]=args['handler']
        for arg in args:
           if arg[0]:
              self._commands[cmd]['short'][arg[0]]=arg
           if arg[1]:
              self._commands[cmd]['long'][arg[1]]=arg
    def getHashed(self,cmd):
        if not cmd in self._commands:
            self.hashCommand(cmd)
        return self._commands[cmd]
            
    def parseArgument(self,argi,prevopt,arg):
            #print "PA",prevopt,arg
            if prevopt:
                return None,((prevopt,arg),)
            elif arg.startswith('--'):
                namevalue=arg[2:].split('=')
                name=namevalue[0]
                if not name in argi['long']:
                    raise CommandParserException('Unknown option %s' % name)
                if argi['long'][name][2]: # option requires an argument
                    if len(namevalue)<2:
                        raise CommandParserException('Option %s requires an argument' % name)
                    value=namevalue[1]
                else:
                    value=True
                return False,((name,value),)
            elif arg.startswith('-'):
                shorts=[]
                for j,c in enumerate(arg[1:]):
                    if prevopt:
                        shorts.append( (prevopt,arg[j+1:]) )
                        prevopt=None
                        break
                    if not c in argi['short']:
                        raise CommandParserException('Unknown short option %s' % c)
                    if not argi['short'][c][2]:
                        shorts.append( (argi['short'][c][1],True) )
                    else:
                        prevopt=argi['short'][c][1]
                return prevopt,shorts

    def formatCommandHelp(self,command):
        return command+':\n'+'\n'.join( (("-"+arg[0]).rjust(4)+(' ARG' if arg[2] else '    ') + \
          ("--"+arg[1]).rjust(10)+('=ARG' if arg[2] else '    ') + \
          ' '+arg[3]) for arg in self.commands['redeye',command]['handler'].arguments)
        pass

    @defer.inlineCallbacks        
    def handleCommand(self,msg):
        command,options,rest = self.parse(msg.body)#unicode(msg.body).encode('utf-8','ignore'))
        try:
            if 'help' in options:
                defer.returnValue((yield self.formatCommandHelp(command.lower())))
            defer.returnValue((yield self.commands['redeye',command.lower()]['handler'](options,rest,msg)))
        except XmppResponse, response:
            defer.returnValue(response)
               

    def parse(self,text):
        #if text[0:1]=='>':
        #    return self.parse('post '+text)
        #elif text[0:1]=='#':
            
        inquotes=None
        firstsym=True
        wordbegin=-1
        prevopt=None
        rest=u''
        waitcommand=True
        options={}
        wordbuf=[] # i know it's ugly and slow. is there any better way to implement quotes?
        for i,c in enumerate(text):
            if c==' ' and not inquotes:
                if len(wordbuf)>0: #1: \todo check why there was 1
                    if waitcommand:
                        waitcommand=False
                        command=''.join(wordbuf).lower()#text[wordbegin:i]
                        if not ('redeye',command) in self.commands:
                            raise CommandParserException('No such command: "%s"' % command)
                        argi=self.getHashed(command)
                    else:
                        prevopt,newopts = self.parseArgument(argi,prevopt,''.join(wordbuf))
                        for name,value in newopts:
                            options[name]=value
                wordbuf=[]
                firstsym=True
            elif c in ('"',"'"):
                if not inquotes:
                    inquotes=c
                elif inquotes==c:
                    inquotes=None
                else:
                    wordbuf.append(c)
            else:
                if firstsym:
                    wordbegin=i
                    firstsym=False
                    if c!='-' and not (prevopt or waitcommand):
                        rest=text[i:]
                        break
                wordbuf.append(c)
        else:
            if inquotes:
                raise CommandParserException("Ouch! You forgot to close quotes <%s> " % inquotes)
            if waitcommand:
                command=''.join(wordbuf).lower()
                if not ('redeye',command) in self.commands:
                    raise CommandParserException('No such command: %s' % command)
            else:
                prevopt,newopts = self.parseArgument(argi,prevopt,''.join(wordbuf))
                if prevopt:
                    raise CommandParserException("Option %s requires an argument" % argi['long'][prevopt][0])
                for name,value in newopts:
                    options[name]=value
        return (command,options,rest)

    
def splitcmd(cmd):
    wordbuf=[]
    inquotes=False
    quotesym=u''
    for i,c in enumerate(cmd):
        if c==' ' and not inquotes:
            yield ''.join(wordbuf)
            wordbuf=[]
        elif c in ('"',"'"):
            if inquotes:
                if c==quotesym:
                    inquotes=False
                else:
                    wordbuf.append(c)
            else:
                inquotes=True
                quotesym=c
        else:
            wordbuf.append(c)
    if len(wordbuf)>0:
        yield ''.join(wordbuf)

