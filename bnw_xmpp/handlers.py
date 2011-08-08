# -*- coding: utf-8 -*-
#from twisted.words.xish import domish

from parser_redeye import RedEyeParser
from parser_regex import RegexParser

import command_bl
import command_clubs
import command_delete
import command_except
import command_help
import command_interface
import command_jids
import command_login
import command_onoff
import command_ping
import command_pm
import command_search
import command_post
import command_register
import command_settings
import command_show
import command_subscription
import command_vcard
import command_userlist
import command_update
import formatters_redeye
import formatters_simple

bl_args = (
                ("u", "user", True, u"Blacklist user."),
                ("t", "tag", True, u"Blacklist tag."),
                ("c", "club", True, u"Blacklist club."),
                ("d", "delete", False, u"Delete blacklist item."),
            )
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
                ('m', 'message',True,'Message or comment to delete.'),
                ('l', 'last',False,'Delete last message or comment.'),
            )
update_args = (
                ('m', 'message',True,'Message or comment to update.'),
                ('c', 'club',False,'Add/delete club.'),
                ('t', 'tag',False,'Add/delete tag.'),
                ('d', 'delete',False,'Delete, not add.'),
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
        ("search", (), command_search.cmd_search, "text", ),
        ("interface", (), command_interface.cmd_interface, "iface", ),
        ("subscribe", subscribe_args, command_subscription.cmd_subscribe, ),
        ("sub", subscribe_args, command_subscription.cmd_subscribe, ),
        ("unsubscribe", subscribe_args, command_subscription.cmd_unsubscribe, ),
        ("usub", subscribe_args, command_subscription.cmd_unsubscribe, ),
        ("subscriptions", (), command_subscription.cmd_subscriptions, ),
        ("lsub", (), command_subscription.cmd_subscriptions, ),
        ("help", (), command_help.cmd_help_redeye, ),
        ("feed", (), command_show.cmd_feed, ),
        ("today", (), command_show.cmd_today, ),
        ("f", (), command_show.cmd_feed, ),
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
        ("bl", bl_args, command_bl.cmd_blacklist, ),
        ("vcard", (), command_vcard.cmd_vcard, ),
        ("pm",
            (
                ("u", "user", True, u"Target user."),
            ),
            command_pm.cmd_pm,
            "text",
        ),
        ("userlist",
            (
                ("p", "page", True, u"Page number."),
            ),
            command_userlist.cmd_userlist,
        ),
        ("update", update_args, command_update.cmd_update, "text", ),
        ("u", update_args, command_update.cmd_update, "text", ),
        ("set",
            (
                ("c", "usercss", True, u"User CSS."),
                ("p", "password", True, u"Password."),
            ),
            command_settings.cmd_set,
        ),
        ("clubs", (), command_clubs.cmd_clubs, ),
        ("jids",
            (
                ("a", "add", True, u"JID to add."),
                ("d", "delete", True, u"JID to delete."),
                ("s", "select", True, u"JID to select."),
            ),
            command_jids.cmd_jids,
        ),
        ("confirm", (), command_jids.cmd_confirm, "code", ),
)

redeye_formatters = {
    'comment': formatters_redeye.formatter_comment,
    'clubs': formatters_redeye.formatter_clubs,
    'message': formatters_redeye.formatter_message,
    'recommendation': formatters_redeye.formatter_recommendation,
    'message_with_replies': formatters_redeye.formatter_message_with_replies,
    'messages': formatters_redeye.formatter_messages,
    'subscriptions': formatters_redeye.formatter_subscriptions,
    'blacklist': formatters_redeye.formatter_blacklist,
    'search': formatters_redeye.formatter_search,
    'userlist': formatters_redeye.formatter_userlist,
    'settings': formatters_redeye.formatter_settings,
    'jids': formatters_redeye.formatter_jids,
}

simple_handlers = (
        (ur'(?:ping|PING|зштп|пинг|ПИНГ)', command_ping.cmd_ping),
        (ur'REGISTER (?P<name>\S+)',command_register.cmd_register),
        (ur'(?:INTERFACE|interface) (?P<iface>\S+)',command_interface.cmd_interface),
        (ur'(?:vcard|VCARD)', command_vcard.cmd_vcard),
        (ur'(?:userlist|USERLIST)(?: (?P<page>\S+))?', command_userlist.cmd_userlist),
        (ur'\? (?P<text>\S+)',command_search.cmd_search),
        (ur'[DdвВ] (?:#|http://bnw.im/p/)(?P<message>.+)',command_delete.cmd_delete),
        (ur'[DdвВ] L',command_delete.cmd_delete,{'last':True}),
        (ur'[SsыЫ]',command_subscription.cmd_subscriptions),
        (ur'[SsыЫ] (?:#|http://bnw.im/p/)(?P<message>.+)',command_subscription.cmd_subscribe),
        (ur'[SsыЫ] (?:@|http://bnw.im/u/)(?P<user>\S+)',command_subscription.cmd_subscribe),
        (ur'[SsыЫ] \*(?P<tag>\S+)',command_subscription.cmd_subscribe),
        (ur'[SsыЫ] !(?P<club>\S+)',command_subscription.cmd_subscribe),
        (ur'[UuгГ] (?:#|http://bnw.im/p/)(?P<message>.+)',command_subscription.cmd_unsubscribe),
        (ur'[UuгГ] (?:@|http://bnw.im/u/)(?P<user>\S+)',command_subscription.cmd_unsubscribe),
        (ur'[UuгГ] \*(?P<tag>\S+)',command_subscription.cmd_unsubscribe),
        (ur'[UuгГ] !(?P<club>\S+)',command_subscription.cmd_unsubscribe),
#        (ur'L @(?P<user>\S+)','not_implemented'),
        (ur'(?:HELP|help)',command_help.cmd_help_simple),
        (ur'(?:LOGIN|login)',command_login.cmd_login),
        (ur'(?:ON|on)',command_onoff.cmd_on),
        (ur'(?:OFF|off)',command_onoff.cmd_off),
        (ur'PM +@(?P<user>\S+) +(?P<text>.+)',command_pm.cmd_pm),

        (ur'BL',command_bl.cmd_blacklist),
        (ur'BL \+?(?:@|http://bnw.im/u/)(?P<user>\S+)',command_bl.cmd_blacklist),
        (ur'BL \+?\*(?P<tag>\S+)',command_bl.cmd_blacklist),
        (ur'BL \+?!(?P<club>\S+)',command_bl.cmd_blacklist),
        (ur'BL -(?:@|http://bnw.im/u/)(?P<user>\S+)',command_bl.cmd_blacklist,{'delete':True}),
        (ur'BL -\*(?P<tag>\S+)',command_bl.cmd_blacklist,{'delete':True}),
        (ur'BL -!(?P<club>\S+)',command_bl.cmd_blacklist,{'delete':True}),

        (ur'JID \+(?P<add>\S+)',command_jids.cmd_jids),
        (ur'JID -(?P<delete>\S+)',command_jids.cmd_jids),
        (ur'JID !(?P<select>\S+)',command_jids.cmd_jids),
        (ur'JID',command_jids.cmd_jids),
        (ur'(?:TODAY|today|Today)',command_show.cmd_today),
        (ur'[#№]',command_show.cmd_feed),
        (ur'[#№]\+',command_show.cmd_show),
        (ur'(?:@|http://bnw.im/u/)(?P<user>\S+)',command_show.cmd_show),
        (ur'(?:@|http://bnw.im/u/)(?P<user>\S+)',command_show.cmd_show),
        (ur'(?:@|http://bnw.im/u/)(?P<user>\S+) \*(?P<tag>\S+)',command_show.cmd_show),
        (ur'\*(?P<tag>\S+)',command_show.cmd_show),
        (ur'!(?P<club>\S+)',command_show.cmd_show),
        (ur'(?:#|http://bnw.im/p/)(?P<message>[0-9A-Za-z]+(?:[/#][0-9A-Za-z]+))',command_show.cmd_show),
        (ur'(?:#|http://bnw.im/p/)(?P<message>[0-9A-Za-z]+)',command_show.cmd_show,{}),
        (ur'(?:#|http://bnw.im/p/)(?P<message>[0-9A-Za-z]+)\+',command_show.cmd_show,{'replies':True}),
        (ur'(?:#|http://bnw.im/p/)(?P<message>[0-9A-Za-z]+) \+!(?P<text>.+)',command_update.cmd_update,{'club':True}),
        (ur'(?:#|http://bnw.im/p/)(?P<message>[0-9A-Za-z]+) \+\*(?P<text>.+)',command_update.cmd_update,{'tag':True}),
        (ur'(?:#|http://bnw.im/p/)(?P<message>[0-9A-Za-z]+) -!(?P<text>.+)',command_update.cmd_update,{'club':True,'delete':True}),
        (ur'(?:#|http://bnw.im/p/)(?P<message>[0-9A-Za-z]+) -\*(?P<text>.+)',command_update.cmd_update,{'tag':True,'delete':True}),
        (ur'(?:#|http://bnw.im/p/)(?P<message>[0-9A-Za-z]+) (?P<text>.+)',command_post.cmd_comment),
        (ur'(?:#|http://bnw.im/p/)(?P<message>[0-9A-Za-z]+[/#][0-9A-Za-z]+) (?P<text>.+)',command_post.cmd_comment),
        (ur'! +(?:#|http://bnw.im/p/)(?P<message>[0-9A-Za-z]+)(?: (?P<comment>.+))?',command_post.cmd_recommend),
        (ur'(?:(?P<tag1>[\*!]\S+)?(?:\s+(?P<tag2>[\*!]\S+))?(?:\s+(?P<tag3>[\*!]\S+))?(?:\s+(?P<tag4>[\*!]\S+))?(?:\s+(?P<tag5>[\*!]\S+))?\s+)?(?P<text>.+)',
            command_post.cmd_post_simple),
    )

simple_formatters = {
    'comment': formatters_simple.formatter_comment,
    'message': formatters_simple.formatter_message,
    'recommendation': formatters_simple.formatter_recommendation,
    'message_with_replies': formatters_simple.formatter_message_with_replies,
    'messages': formatters_simple.formatter_messages,
    'subscriptions': formatters_redeye.formatter_subscriptions,
    'blacklist': formatters_redeye.formatter_blacklist,
    'search': formatters_redeye.formatter_search,
    'userlist': formatters_simple.formatter_userlist,
    'jids': formatters_redeye.formatter_jids,
}

parsers={}
parsers['redeye']=RedEyeParser(redeye_handlers,redeye_formatters)
parsers['simplified']=RegexParser(simple_handlers,simple_formatters)

s2s_handlers = {}
