# -*- coding: utf-8 -*-

from parser_redeye import RedEyeParser
from parser_regex import RegexParser

from bnw.handlers import command_alias
from bnw.handlers import command_bl
from bnw.handlers import command_clubs
from bnw.handlers import command_delete
from bnw.handlers import command_except
from bnw.handlers import command_help
from bnw.handlers import command_interface
from bnw.handlers import command_jids
from bnw.handlers import command_login
from bnw.handlers import command_onoff
from bnw.handlers import command_ping
from bnw.handlers import command_pm
from bnw.handlers import command_search
from bnw.handlers import command_post
from bnw.handlers import command_register
from bnw.handlers import command_settings
from bnw.handlers import command_show
from bnw.handlers import command_subscription
from bnw.handlers import command_vcard
from bnw.handlers import command_userlist
from bnw.handlers import command_update
import formatters_redeye
import formatters_simple

# -h / --help is defined and handled in redeye parser itself. Put nice, short
# option descriptions into fourth element of a tuple and you'll be fine.
bl_args = (
                ("u", "user", True, u"Blacklist user"),
                ("t", "tag", True, u"Blacklist tag"),
                ("c", "club", True, u"Blacklist club"),
                ("d", "delete", False, u"Delete existing item"),
            )
subscribe_args = (
                ("m", "message", True, u"Subscribe to message."),
                ("u", "user", True, u"Subscribe to user."),
                ("t", "tag", True, u"Subscribe to tag."),
                ("c", "club", True, u"Subscribe to club."),
                ("n", "newtab", False, u"Receive messages for this subscription from into tab"),
            )
show_args =  (
                ("m", "message", True, u"Show specified message"),
                ("u", "user", True, u"Show user's posts"),
                ("t", "tag", True, u"Show posts with tag"),
                ("c", "club", True, u"Show club posts"),
                ("p", "page", True, u"Show nth results page (counting from 0)"),
                ("r", "replies", False, u"Show replies as well (only with -m)"),
                ("b", "before", True, u"Show replies older than this one"),
                ("a", "after", True, u"Show replies newer than this one"),
                ("", "use_bl", False, u"Don't show messages from BL'ed users"),
            )
post_args = (
                ("s", "notop", False, u"Post cannot be bumped to top"), # no-op
                ("t", "tags", True, u"Mark post with this tag(s) (comma-separated)"),
                ("c", "clubs", True, u"Post to this club(s) (comma-separated)"),
                ("a", "anonymous", False, u"Anonymous post"),
                ("q", "anoncomments", False, u"Make all comments to this post anonymous"),
                ("f", "format", True, u"Specify the formatting used (one of: %s)" % command_post.acceptable_formats_str)
            )
comment_args = (
                ("m", "message", True, u"Message to comment"),
                ("a", "anonymous", False, u"Anonymous comment"),
                ("f", "format", True, u"Specify the formatting used (one of: %s)" % command_post.acceptable_formats_str)
            )
recommend_args = (
                ("m", "message", True, u"Message to recommend"),
                ("u", "unrecommend", False, u"Delete message from your recommendations list"),
            )
delete_args = (
                ('m', 'message',True,'Message or comment to delete'),
                ('l', 'last',False,'Delete your last message or comment'),
            )
update_args = (
                ('m', 'message',True,'Message or comment to update'),
                ('c', 'club',False,'Post to/delete from the club'),
                ('t', 'tag',False,'Add/delete tag'),
                ('d', 'delete',False,'Delete, not add'),
                ('', 'clubs', True, 'Set comma-separated list of clubs'),
                ('', 'tags', True, 'Set comma-separated list of tags'),
                # ('', 'api', False, 'Set clubs and tags using api'),
                ("f", "format", True, u"Set the formatting used (one of: %s)" % command_post.acceptable_formats_str)
            )
feed_args = (
                ("p", "page", True, u"Show nth results page (counting from 0)"),
            )

redeye_standard_aliases = {
    "subscribe":     "sub"
,   "unsubscribe":   "usub"
,   "subscriptions": "lsub"
,   "feed":          "f"
,   "show":          "s"
,   "post":          "p"
,   "comment":       "c"
,   "recommend":     "r"
,   "delete":        "d"
,   "update":        "u"
}

redeye_handlers = (
        ("ping",
            (
                ("s", "safe", False, u"Do not vyebyvatsya."),
            ),
            command_ping.cmd_ping,
        ),

#        ("except", (), command_except.cmd_except, ),
        ("register", (), command_register.cmd_register, "name", ),
        ("search",
            (
                ("p", "page", True, u"Show nth results page (counting from 0)"),
            ),
            command_search.cmd_search, "query", ),
        ("interface", (), command_interface.cmd_interface, "iface", ),
        ("subscribe", subscribe_args, command_subscription.cmd_subscribe, ),
        ("unsubscribe", subscribe_args, command_subscription.cmd_unsubscribe, ),
        ("subscriptions", (), command_subscription.cmd_subscriptions, ),
        ("help", (), command_help.cmd_help_redeye, ),
        ("feed", feed_args, command_show.cmd_feed, ),
        ("today",
            (
                ("", "use_bl", False, u"Don't show messages from BL'ed users"),
            ),
            command_show.cmd_today, ),
        ("show", show_args, command_show.cmd_show, ),
        ("post", post_args, command_post.cmd_post, "text", ),
        ("comment", comment_args, command_post.cmd_comment, "text", ),
        ("recommend", recommend_args, command_post.cmd_recommend, "comment", ),
        ("on", (), command_onoff.cmd_on, ),
        ("off", (), command_onoff.cmd_off, ),
        ("delete", delete_args, command_delete.cmd_delete, ),
        ("login",
            (
                ("r", "reset", False, u"Reset login key"),
            ),
            command_login.cmd_login, ),
        ("bl", bl_args, command_bl.cmd_blacklist, ),
        ("vcard", (), command_vcard.cmd_vcard, ),
        ("pm",
            (
                ("u", "user", True, u"Target user"),
            ),
            command_pm.cmd_pm,
            "text",
        ),
        ("userlist",
            (
                ("p", "page", True, u"Show nth results page (counting from 0)"),
            ),
            command_userlist.cmd_userlist,
        ),
        ("update", update_args, command_update.cmd_update, "text", ),
        ("set",
            (
                ("c", "usercss", True, u"User CSS"),
                ("p", "password", True, u"Password"),
                ("s", "servicejid", False, u"Set service's jid"),
                ("b", "baseurl", True, u"Set base url for links"),
                ("a", "about", True, u'Set "about me"'),
                ("", "notify_on_recommendation", True, u'Set "notify_on_recommendation"'),
                ("f", "default_format", True, u"Default formatting for posts and comments (one of: %s)" % command_post.acceptable_formats_str),
            ),
            command_settings.cmd_set,
        ),
        ("clubs", (), command_clubs.cmd_clubs, ),
        ("jids",
            (
                ("a", "add", True, u"JID to add"),
                ("d", "delete", True, u"JID to delete"),
                ("s", "select", True, u"JID to select"),
            ),
            command_jids.cmd_jids,
        ),
        ("confirm", (), command_jids.cmd_confirm, "code", ),
        ("alias",
            (
                ("d", "delete", True, u"Delete an alias"),
                ("s", "set", True, u"Update an alias"),
            ),
            command_alias.cmd_alias,
            'value',
        ),
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
        (ur'(?i)(?:ping|зштп|пинг)', command_ping.cmd_ping),
        (ur'(?i)register (?P<name>\S+)',command_register.cmd_register),
        (ur'(?i)interface (?P<iface>\S+)',command_interface.cmd_interface),
        (ur'(?i)vcard', command_vcard.cmd_vcard),
        (ur'(?i)userlist(?: (?P<page>\S+))?', command_userlist.cmd_userlist),
        (ur'\? (?P<query>.+)',command_search.cmd_search),
        (ur'(?i)[DВ] [#№](?P<message>.+)',command_delete.cmd_delete),
        (ur'(?i)[DВ] L',command_delete.cmd_delete,{'last':True}),
        (ur'(?i)[SЫ]',command_subscription.cmd_subscriptions),
        (ur'(?i)[SЫ] [#№](?P<message>.+)',command_subscription.cmd_subscribe),
        (ur'(?i)[SЫ] @(?P<user>\S+)',command_subscription.cmd_subscribe),
        (ur'(?i)[SЫ] \*(?P<tag>\S+)',command_subscription.cmd_subscribe),
        (ur'(?i)[SЫ] !(?P<club>\S+)',command_subscription.cmd_subscribe),
        (ur'(?i)[UГ] [#№](?P<message>.+)',command_subscription.cmd_unsubscribe),
        (ur'(?i)[UГ] @(?P<user>\S+)',command_subscription.cmd_unsubscribe),
        (ur'(?i)[UГ] \*(?P<tag>\S+)',command_subscription.cmd_unsubscribe),
        (ur'(?i)[UГ] !(?P<club>\S+)',command_subscription.cmd_unsubscribe),
#        (ur'L @(?P<user>\S+)','not_implemented'),
        (ur'(?i)help',command_help.cmd_help_simple),
        (ur'(?i)login',command_login.cmd_login),
        (ur'(?i)on',command_onoff.cmd_on),
        (ur'(?i)off',command_onoff.cmd_off),
        (ur'(?i)pm +@(?P<user>\S+)\s+(?P<text>.+)',command_pm.cmd_pm),

        (ur'(?i)bl',command_bl.cmd_blacklist),
        (ur'(?i)bl \+?@(?P<user>\S+)',command_bl.cmd_blacklist),
        (ur'(?i)bl \+?\*(?P<tag>\S+)',command_bl.cmd_blacklist),
        (ur'(?i)bl \+?!(?P<club>\S+)',command_bl.cmd_blacklist),
        (ur'(?i)bl -@(?P<user>\S+)',command_bl.cmd_blacklist,{'delete':True}),
        (ur'(?i)bl -\*(?P<tag>\S+)',command_bl.cmd_blacklist,{'delete':True}),
        (ur'(?i)bl -!(?P<club>\S+)',command_bl.cmd_blacklist,{'delete':True}),

        (ur'(?i)jid \+(?P<add>\S+)',command_jids.cmd_jids),
        (ur'(?i)jid -(?P<delete>\S+)',command_jids.cmd_jids),
        (ur'(?i)jid !(?P<select>\S+)',command_jids.cmd_jids),
        (ur'(?i)jid',command_jids.cmd_jids),

        (ur'(?i)set',command_settings.cmd_set),
        (ur'(?i)set +(?P<name>\w+)(?: +(?P<value>.+))?',command_settings.cmd_set),

        (ur'(?i)today',command_show.cmd_today),
        (ur'[#№]',command_show.cmd_feed),
        (ur'[#№]\+',command_show.cmd_show),
        (ur'@(?P<user>\S+)',command_show.cmd_show),
        (ur'@(?P<user>\S+)',command_show.cmd_show),
        (ur'@(?P<user>\S+) \*(?P<tag>\S+)',command_show.cmd_show),
        (ur'\*(?P<tag>\S+)',command_show.cmd_show),
        (ur'!(?P<club>\S+)',command_show.cmd_show),
        (ur'[#№](?P<message>[0-9A-Za-z]+(?:[/#][0-9A-Za-z]+))',command_show.cmd_show),
        (ur'[#№](?P<message>[0-9A-Za-z]+)',command_show.cmd_show,{}),
        (ur'[#№](?P<message>[0-9A-Za-z]+)\+',command_show.cmd_show,{'replies':True}),
        (ur'[#№](?P<message>[0-9A-Za-z]+) \+!(?P<text>.+)',command_update.cmd_update,{'club':True}),
        (ur'[#№](?P<message>[0-9A-Za-z]+) \+\*(?P<text>.+)',command_update.cmd_update,{'tag':True}),
        (ur'[#№](?P<message>[0-9A-Za-z]+) -!(?P<text>.+)',command_update.cmd_update,{'club':True,'delete':True}),
        (ur'[#№](?P<message>[0-9A-Za-z]+) -\*(?P<text>.+)',command_update.cmd_update,{'tag':True,'delete':True}),
        (ur'[#№](?P<message>[0-9A-Za-z]+)\s(?P<text>.+)',command_post.cmd_comment),
        (ur'(?P<anonymous>ANON\s+)[#№](?P<message>[0-9A-Za-z]+)\s(?P<text>.+)',command_post.cmd_comment),
        (ur'[#№](?P<message>[0-9A-Za-z]+)[/#](?P<after>[0-9A-Za-z]+)\+',command_show.cmd_show,{'replies':True}),
        (ur'[#№](?P<message>[0-9A-Za-z]+[/#][0-9A-Za-z]+)\s(?P<text>.+)',command_post.cmd_comment),
        (ur'(?P<anonymous>ANON\s+)[#№](?P<message>[0-9A-Za-z]+[/#][0-9A-Za-z]+)\s(?P<text>.+)',command_post.cmd_comment),
        (ur'! +[#№](?P<message>[0-9A-Za-z]+)(?: (?P<comment>.+))?',command_post.cmd_recommend),
        (ur'!(?P<unrecommend>!) +[#№](?P<message>[0-9A-Za-z]+)',command_post.cmd_recommend),
        (ur'(?:(?P<anonymous>ANON|ФТЩТ)(?:\s+(?P<tag1>[\*!]\S+))?(?:\s+(?P<tag2>[\*!]\S+))?(?:\s+(?P<tag3>[\*!]\S+))?(?:\s+(?P<tag4>[\*!]\S+))?(?:\s+(?P<tag5>[\*!]\S+))?\s+)?(?P<text>.+)',
            command_post.cmd_post_simple),
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
    'settings': formatters_redeye.formatter_settings,
    'jids': formatters_redeye.formatter_jids,
}

parsers={}
parsers['redeye']=RedEyeParser(redeye_handlers, redeye_standard_aliases, redeye_formatters)
parsers['simplified']=RegexParser(simple_handlers,simple_formatters)

s2s_handlers = {}
