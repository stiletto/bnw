from bnw_handlers import command_clubs
from bnw_handlers import command_delete
from bnw_handlers import command_except
from bnw_handlers import command_help
from bnw_handlers import command_interface
from bnw_handlers import command_login
from bnw_handlers import command_onoff
from bnw_handlers import command_ping
from bnw_handlers import command_pm
from bnw_handlers import command_search
from bnw_handlers import command_post
from bnw_handlers import command_register
from bnw_handlers import command_show
from bnw_handlers import command_subscription
from bnw_handlers import command_vcard
from bnw_handlers import command_userlist
from bnw_handlers import command_bl
from bnw_handlers import command_stat
from bnw_handlers import command_update


# TODO: Auto-import all avialable handlers?
handlers = {
    "register":             command_register.cmd_register,
    "search":               command_search.cmd_search,
    "interface":            command_interface.cmd_interface,
    "subscriptions/add":    command_subscription.cmd_subscribe,
    "subscriptions/del":    command_subscription.cmd_unsubscribe,
    "subscriptions":        command_subscription.cmd_subscriptions,
    "feed":                 command_show.cmd_feed,
    "today":                command_show.cmd_today,
    "show":                 command_show.cmd_show,
    "post":                 command_post.cmd_post,
    "comment":              command_post.cmd_comment,
    "recommend":            command_post.cmd_recommend,
    "on":                   command_onoff.cmd_on,
    "off":                  command_onoff.cmd_off,
    "delete":               command_delete.cmd_delete,
    "pm":                   command_pm.cmd_pm,
    "userlist":             command_userlist.cmd_userlist,
    "vcard":                command_vcard.cmd_vcard,
    "clubs":                command_clubs.cmd_clubs,
    "tags":                 command_clubs.cmd_tags,
    "passlogin":            command_login.cmd_passlogin,
    "blacklist":            command_bl.cmd_blacklist,
    "stat":                 command_stat.cmd_stat,
    "update":               command_update.cmd_update,
}
