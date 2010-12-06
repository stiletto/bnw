# -*- coding: utf-8 -*-
#from twisted.words.xish import domish
from base import XmppResponse

from parser_redeye import RedEyeParser
from parser_regex import RegexParser

import command_delete
import command_except
import command_help
import command_interface
import command_login
import command_onoff
import command_ping
import command_post
import command_register
import command_show
import command_subscription
import formatters_redeye

subscribe_args = (
                ("m", "message", True, u"Subscribe to message."),
                ("u", "user", True, u"Subscribe to user."),
                ("t", "tag", True, u"Subscribe to tag."),
                ("c", "club", True, u"Subscribe to club."),
                ("n", "newtab", False, u"Receive messages for this subscription from into tab"),
            )
show_args =  (
                ("m", "message", True, u"Show specified message."),
                ("u", "user", True, u"Show user's posts."),
                ("t", "tag", True, u"Show posts with tag."),
                ("c", "club", True, u"Show club posts."),
                ("p", "page", True, u"Results page (from 0)."),
                ("r", "replies", False, u"Include replies in output (only with -m)."),
            )
post_args = (
                ("s", "notop", False, u"Post cannot be bumped to top."), # no-op
                ("t", "tags", True, u"Mark post with this tag(s) (comma-separated)."),
                ("c", "clubs", True, u"Post to this club(s) (comma-separated)."),
                ("a", "anonymous", False, u"Anonymous post."),
                ("q", "anonymous-comments", False, u"Make all comments to this post anonymous (doesn''t work at all yet)."),
            )
comment_args = (
                ("m", "message", True, u"Message to comment."),
                ("a", "anonymous", False, u"Anonymous comment."),
            )
recommend_args = (
                ("m", "message", True, u"Message to recommend."),
            )
delete_args = (
                ('m',   'message',True,'Message or comment to delete.'),
            )

redeye_handlers = (
        ("ping", 
            (
                ("s", "safe", False, u"Do not vyebyvatsya."),
            ),
            command_ping.cmd_ping,
        ),

#        ("except", (), , ),
        ("register", (), command_register.cmd_register, "name", ),
        ("interface", (), command_interface.cmd_interface, "iface", ),
        ("subscribe", subscribe_args, command_subscription.cmd_subscribe, ),
        ("sub", subscribe_args, command_subscription.cmd_subscribe, ),
        ("unsubscribe", subscribe_args, command_subscription.cmd_unsubscribe, ),
        ("usub", subscribe_args, command_subscription.cmd_unsubscribe, ),
        ("subscriptions", (), command_subscription.cmd_subscriptions, ),
        ("lsub", (), command_subscription.cmd_subscriptions, ),
        ("help", (), command_help.cmd_help_redeye, ),
        ("show", show_args, command_show.cmd_show, ),
        ("s", show_args, command_show.cmd_show, ),
        ("post", post_args, command_post.cmd_post, "text", ),
        ("p", post_args, command_post.cmd_post, "text", ),
        ("comment", comment_args, command_post.cmd_comment, "text", ),
        ("c",  comment_args, command_post.cmd_comment, "text", ),
        ("recommend", recommend_args, command_post.cmd_recommend, "comment", ),
        ("r", recommend_args, command_post.cmd_recommend, "comment", ),
        ("on", (), command_onoff.cmd_on, ),
        ("off", (), command_onoff.cmd_off, ),
        ("delete", delete_args, command_delete.cmd_delete, ),
        ("d", delete_args, command_delete.cmd_delete, ),
        ("login", (), command_login.cmd_login, ),
)

redeye_formatters = {
    'comment': formatters_redeye.formatter_comment,
    'message': formatters_redeye.formatter_message,
    'recommendation': formatters_redeye.formatter_recommendation,
    'message_with_replies': formatters_redeye.formatter_message_with_replies,
    'messages': formatters_redeye.formatter_messages,
    'subscriptions': formatters_redeye.formatter_subscriptions,
}

simple_handlers = (
        (ur'(?:ping|PING|зштп|пинг|ПИНГ)', 'ping'),
        (ur'REGISTER (?P<name>\S+)',command_register.cmd_register),
        (ur'(?:INTERFACE|interface) (?P<iface>\S+)',command_interface.cmd_interface),
        (ur'[DdвВ] #(?P<message>.+)',command_delete.cmd_delete),
        (ur'[DdвВ] L',command_delete.cmd_delete,{'last':True}),
        (ur'[SsыЫ]',command_subscription.cmd_subscriptions),
        (ur'[SsыЫ] @(?P<user>\S+)',command_subscription.cmd_subscribe),
        (ur'[SsыЫ] \*(?P<tag>\S+)',command_subscription.cmd_subscribe),
        (ur'[SsыЫ] !(?P<club>\S+)',command_subscription.cmd_subscribe),
        (ur'[UuгГ] @(?P<user>\S+)',command_subscription.cmd_unsubscribe),
        (ur'[UuгГ] \*(?P<tag>\S+)',command_subscription.cmd_unsubscribe),
        (ur'[UuгГ] !(?P<club>\S+)',command_subscription.cmd_unsubscribe),
        (ur'L @(?P<user>\S+)','not_implemented'),
        (ur'(?:HELP|help)',command_help.cmd_help_simple),
        (ur'(?:LOGIN|login)',command_login.cmd_login),
        (ur'(?:ON|on)',command_onoff.cmd_on),
        (ur'(?:OFF|off)',command_onoff.cmd_off),
#        (r'PM +@(?P<user>\S+) +(?P<text>.+)',command_pm.cmd_pm),
        (ur'BL','not_implemented'),
        (ur'BL .+','not_implemented'),
        (ur'\? .+','not_implemented'),
        (ur'[#№]','feed'),
        (ur'[#№]\+',command_show.cmd_show),
        (ur'@(?P<user>\S+)',command_show.cmd_show),
        (ur'@(?P<user>\S+)',command_show.cmd_show),
        (ur'@(?P<user>\S+) \*(?P<tag>\S+)',command_show.cmd_show),
        (ur'\*(?P<tag>\S+)',command_show.cmd_show),
        (ur'!(?P<club>\S+)',command_show.cmd_show),
        (ur'#(?P<message>[0-9A-Za-z]+)',command_show.cmd_show),
        (ur'#(?P<message>[0-9A-Za-z]+)\+',command_show.cmd_show,{'replies':True}),
        (ur'#(?P<message>[0-9A-Za-z]+) (?P<text>.+)',command_post.cmd_comment),
        (ur'#(?P<message>[0-9A-Za-z]+/[0-9A-Za-z]+) (?P<text>.+)',command_post.cmd_comment),
        (ur'! +#(?P<message>[0-9A-Za-z]+)(?: (?P<comment>.+))?',command_post.cmd_recommend),
        (ur'(?:(?P<tag1>[\*!]\S+)?(?: (?P<tag2>[\*!]\S+))?(?: (?P<tag3>[\*!]\S+))?(?: (?P<tag4>[\*!]\S+))?(?: (?P<tag5>[\*!]\S+))? )?(?P<text>.+)',
            command_post.cmd_post),
    )

simple_formatters = {
    'comment': formatters_redeye.formatter_comment,
    'message': formatters_redeye.formatter_message,
    'recommendation': formatters_redeye.formatter_recommendation,
    'message_with_replies': formatters_redeye.formatter_message_with_replies,
    'messages': formatters_redeye.formatter_messages,
    'subscriptions': formatters_redeye.formatter_subscriptions,
}

parsers={}
parsers['redeye']=RedEyeParser(redeye_handlers,redeye_formatters)
parsers['simplified']=RegexParser(simple_handlers,simple_formatters)
