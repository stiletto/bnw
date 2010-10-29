# -*- coding: utf-8 -*-
#from twisted.words.xish import domish
from base import XmppResponse

from parser_redeye import RedEyeParser
from parser_simplified import SimplifiedParser
from command_registry import CommandRegistry#,Command

commands=CommandRegistry()

parsers={}
parsers['redeye']=RedEyeParser(commands)
parsers['simplified']=SimplifiedParser(commands)

commands.registerCommand('bnw_xmpp.command_ping',redeye={'name':'ping','handler':'cmd.handleRedeye'},
        simplified={'name':'PING','handler':'cmd.handleSimplified'})

commands.registerCommand('bnw_xmpp.command_register',redeye={'name':'register','handler':'cmd.handleRedeye'})

commands.registerCommand('bnw_xmpp.command_interface',redeye={'name':'interface','handler':'cmd.handleRedeye'},
        simplified={'name':'INTERFACE','handler':'cmd.handleSimplified'})

commands.registerCommand('bnw_xmpp.command_subscription',redeye={'name':'subscribe','handler':'sub.handleRedeye'},
        simplified={'name':'S','handler':'sub.handleSimplified'})
commands.registerCommand('bnw_xmpp.command_subscription',redeye={'name':'sub','handler':'sub.handleRedeye'})

commands.registerCommand('bnw_xmpp.command_subscription',redeye={'name':'unsubscribe','handler':'usub.handleRedeye'},
        simplified={'name':'U','handler':'usub.handleSimplified'})
commands.registerCommand('bnw_xmpp.command_subscription',redeye={'name':'usub','handler':'usub.handleRedeye'})

commands.registerCommand('bnw_xmpp.command_subscription',redeye={'name':'subscriptions','handler':'lsub.handleRedeye'})
commands.registerCommand('bnw_xmpp.command_subscription',redeye={'name':'lsub','handler':'lsub.handleRedeye'})

commands.registerCommand('bnw_xmpp.command_help',redeye={'name':'help','handler':'cmd.handleRedeye'},
        simplified={'name':'HELP','handler':'cmd.handleSimplified'})

commands.registerCommand('bnw_xmpp.command_show',redeye={'name':'show','handler':'cmd.handleRedeye'},
        simplified={'name':'show','handler':'cmd.handleSimplified'})
commands.registerCommand('bnw_xmpp.command_show',redeye={'name':'s','handler':'cmd.handleRedeye'})

commands.registerCommand('bnw_xmpp.command_post',redeye={'name':'post','handler':'postcmd.handleRedeye'},
        simplified={'name':'post','handler':'postcmd.handleSimplified'})
commands.registerCommand('bnw_xmpp.command_post',redeye={'name':'p','handler':'postcmd.handleRedeye'})

commands.registerCommand('bnw_xmpp.command_post',redeye={'name':'comment','handler':'commentcmd.handleRedeye'},
        simplified={'name':'reply','handler':'commentcmd.handleSimplified'})
commands.registerCommand('bnw_xmpp.command_post',redeye={'name':'c','handler':'commentcmd.handleRedeye'})

commands.registerCommand('bnw_xmpp.command_onoff',redeye={'name':'on','handler':'oncmd.handleRedeye'},
        simplified={'name':'ON','handler':'oncmd.handleSimplified'})
commands.registerCommand('bnw_xmpp.command_onoff',redeye={'name':'off','handler':'offcmd.handleRedeye'},
        simplified={'name':'OFF','handler':'offcmd.handleSimplified'})

commands.registerCommand('bnw_xmpp.command_delete',redeye={'name':'delete','handler':'cmd.handleRedeye'},
        simplified={'name':'D','handler':'cmd.handleSimplified'})
commands.registerCommand('bnw_xmpp.command_delete',redeye={'name':'d','handler':'cmd.handleRedeye'})
