# coding: utf-8

from twisted.internet import defer, reactor
import re

def sendText(fac, me, text, reset=True):
    fac.stanzaReset()
    fac.stanzaSend("""<message type='chat' from='%s' to='bnw.test'>
        <body>%s</body></message>""" % (me, text,))

def compareBody(msg, body):
    if msg.body:
        text = unicode(msg.body).encode('utf-8','replace')
        match = re.match('^'+body+'$', text, re.DOTALL)
        if match:
            return match.groups()
    raise Exception('No match: '+body)


empty_png = """iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAACXBIWXMAAAsTAAALEwEAmpwYAAAA
B3RJTUUH3gkOADQKUtDYVAAAAAxJREFUCNdj+P//PwAF/gL+3MxZ5wAAAABJRU5ErkJggg=="""

markdown_text = """
# Epic title
Some http://i.imgur.com/SU8FkZN.gif fucking
just epic http://example.com/someshit.png shit
![there is no image](http://support.com)
> sucks to write this text

    void code() {
        printf("hui");
    }
```bash
    echo fenced code!
```
Hai @user #message
"""

moinmoin_text = """
Some http://i.imgur.com/SU8FkZN.gif fucking
just epic http://example.com/someshit.png shit
[[http://eto.com|Govno]] www.google.com
> **sucks** to // **write //this// text

{{{#!bash
    echo fenced code!
}}}
Hai @user #message
"""

def deferSleep(time):
    d = defer.Deferred()
    reactor.callLater(time, d.callback, None)
    return d
@defer.inlineCallbacks
def startTests(factory):
    import sys
    sys = reload(sys)
    sys.setdefaultencoding('utf-8')
    me = 'hui@example.com'
    me2 = 'her@example.org'

    sendText(factory, me, 'ping')
    compareBody((yield factory.stanzaRecv()), 'ERROR. Only for registered users')


    sendText(factory, me, 'register test1')
    compareBody((yield factory.stanzaRecv()), 'OK. We registered you as test1.')

    sendText(factory, me2, 'register test2')
    compareBody((yield factory.stanzaRecv()), 'OK. We registered you as test2.')

    sendText(factory, me, 'help')
    compareBody((yield factory.stanzaRecv()), 'OK. .*')

    sendText(factory, me, 'sub -u test3')
    compareBody((yield factory.stanzaRecv()), 'ERROR. No such user.')

    sendText(factory, me, 'sub -u test2')
    compareBody((yield factory.stanzaRecv()), '@test1 subscribed to your blog. http://localhost:9782/u/test1')
    compareBody((yield factory.stanzaRecv()), 'OK. Subscribed.')

    sendText(factory, me, 'sub -m AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
    compareBody((yield factory.stanzaRecv()), 'ERROR. No such message.')

    sendText(factory, me, 'c -am HUX2KJ/2BB ""')
    compareBody((yield factory.stanzaRecv()), 'ERROR. So where is your comment\?')

    msgid = []
    for x in range(2):
        sendText(factory, me, 'post --format=md --tags=hui,pizda --clubs=jigurda %s' % (markdown_text,))
        msgid.append(compareBody((yield factory.stanzaRecv()), 'OK. Message #([A-Z0-9]+) has been delivered to 0 users. http://localhost:9782/p/.*')[0])

    sendText(factory, me, 'usub -m %s' % (msgid[1],))
    compareBody((yield factory.stanzaRecv()), 'OK. Unsubscribed.')
    sendText(factory, me, 'sub -m %s' % (msgid[1],))
    compareBody((yield factory.stanzaRecv()), 'OK. Subscribed \(0 replies\).')

    sendText(factory, me2, 'sub -m %s' % (msgid[1],))
    compareBody((yield factory.stanzaRecv()), 'OK. Subscribed \(0 replies\).')

    sendText(factory, me2, 'sub -u test1')
    compareBody((yield factory.stanzaRecv()), '@test2 subscribed to your blog. http://localhost:9782/u/test2')
    compareBody((yield factory.stanzaRecv()), 'OK. Subscribed.')

    comid = []
    for x in range(2):
        sendText(factory, me, 'c -f mm -m %s %s' % (msgid[1],moinmoin_text))
        comid.append(compareBody((yield factory.stanzaRecv()), 'OK. Comment #([A-Z0-9/]+) \(.\) has been delivered to 1 users. http://localhost:9782/p/.+')[0])
        compareBody((yield factory.stanzaRecv()), '\n\+\+\+ .*')

    sendText(factory, me, 'd -m %s' % (comid[1],))
    compareBody((yield factory.stanzaRecv()), 'OK. Comment %s removed.' % (comid[1],))

    sendText(factory, me, 'd -l')
    compareBody((yield factory.stanzaRecv()), 'OK. Comment %s removed.' % (comid[0],))

    sendText(factory, me, 'd -l')
    compareBody((yield factory.stanzaRecv()), 'OK. Message %s removed.' % (msgid[1],))

    sendText(factory, me, 'alias')
    compareBody((yield factory.stanzaRecv()), 'ERROR. Usage: .*')
    sendText(factory, me, 'alias --set=fuck pm -u %1 %2')
    compareBody((yield factory.stanzaRecv()), 'OK. Alias fuck updated.')

    sendText(factory, me, 'fuck test2 fuck ya')
    compareBody((yield factory.stanzaRecv()), 'OK. PM sent.')
    compareBody((yield factory.stanzaRecv()), 'PM from @test1:.fuck ya')

    #sendText(factory, me, 'pm -u test2 fuck ')
    #compareBody((yield factory.stanzaRecv()), 'You are sending messages too fast! Please wait 5 seconds before trying again.')
    #yield deferSleep(6)
    sendText(factory, me, 'fuck test2 fuck '+('A'*2049))
    compareBody((yield factory.stanzaRecv()), 'ERROR. Too long.')

    sendText(factory, me, 'fuck test4 fuck')
    compareBody((yield factory.stanzaRecv()), 'ERROR. No such user.')

    sendText(factory, me, 'alias --delete=fuck')
    compareBody((yield factory.stanzaRecv()), 'OK. Alias fuck deleted.')

    sendText(factory, me, 'post -t hui,pizda -c @,jigurda fuck ya')
    compareBody((yield factory.stanzaRecv()), 'OK. Message #([A-Z0-9]+) has been delivered to 1 users. http://localhost:9782/p/.*')
    compareBody((yield factory.stanzaRecv()), '\n\+\+\+ .*')


#        cmd, replies = test[0], test[1:]
#        factory.stanzaSend("""<message type='chat' from='hui@example.com' to='bnw.test'>
#            <body>%s</body></message>""" % (cmd,))
#        for reply in replies:
#            msg = yield factory.stanzaRecv()
#            assert compareBody(msg, reply), (u'%s != %s' % (reply, msg.body))
