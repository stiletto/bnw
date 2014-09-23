# -*- coding: utf-8 -*-
from parser_redeye import *

if __name__ == "__main__":
    # This is some sort of parser test.

    subscribe_args = (
        ("m", "message", True, u"Subscribe to message."),
        ("u", "user", True, u"Subscribe to user."),
        ("t", "tag", True, u"Subscribe to tag."),
        ("c", "club", True, u"Subscribe to club."),
        ("n", "newtab", False,
         u"Receive messages for this subscription from into tab"),
    )
    show_args = (
                ("m", "message", True, u"Show specified message."),
                ("u", "user", True, u"Show user's posts."),
                ("t", "tag", True, u"Show posts with tag."),
                ("c", "club", True, u"Show club posts."),
                ("p", "page", True, u"Results page (from 0)."),
                ("r", "replies", False,
                 u"Include replies in output (only with -m)."),
    )
    post_args = (
                ("s", "notop", False,
                 u"Post cannot be bumped to top."),  # no-op
                ("t", "tags", True,
                 u"Mark post with this tag(s) (comma-separated)."),
                ("c", "clubs", True,
                 u"Post to this club(s) (comma-separated)."),
                ("a", "anonymous", False, u"Anonymous post."),
                ("q", "anonymous-comments", False,
                 u"Make all comments to this post anonymous (doesn''t work at all yet)."),
    )
    comment_args = (
        ("m", "message", True, u"Message to comment."),
        ("a", "anonymous", False, u"Anonymous comment."),
    )
    recommend_args = (
        ("m", "message", True, u"Message to recommend."),
    )
    delete_args = (
        ('m', 'message', True, 'Message or comment to delete.'),
    )

    handlers = (
        ("ping",
            (
                ("s", "safe", False, u"Do not vyebyvatsya."),
            ),
            "ping",
         ),

        ("except", (), "except", ),
        ("register", (), "register", "name", ),
        ("interface", (), "interface", "iface", ),
        ("subscribe", subscribe_args, "subscribe", ),
        ("sub", subscribe_args, "subscribe", ),
        ("unsubscribe", subscribe_args, "unsubscribe", ),
        ("usub", subscribe_args, "unsubscribe", ),
        ("subscriptions", (), "subscriptions", ),
        ("lsub", (), "subscriptions", ),
        ("help", (), "help", ),
        ("show", show_args, "show", ),
        ("s", show_args, "show", ),
        ("post", post_args, "post", "text", ),
        ("p", post_args, "post", "text", ),
        ("comment", comment_args, "comment", "text", ),
        ("c", comment_args, "comment", "text", ),
        ("recommend", recommend_args, "recommend", "comment", ),
        ("r", recommend_args, "recommend", "comment", ),
        ("on", (), "on", ),
        ("off", (), "off", ),
        ("delete", delete_args, "delete", ),
        ("d", delete_args, "delete", ),
        ("login", (), "login", ),
    )

    p = RedEyeParser(handlers, {}, [])
    test = (
        ("post --tags=linux,anime,mplayer ваш ляликс - говно для просмотра аниме!",
            ("post", "text", {"tags": "linux,anime,mplayer"}, "ваш ляликс - говно для просмотра аниме!")),
        ("comment -m 123456 ТЫ ГОВНО",
            ("comment", "text", {"message": "123456"}, "ТЫ ГОВНО")),
        ("c --message=123456/123",
            ("comment", "text", {"message": "123456/123"}, "")),
        ("subscribe -t mytag",
            ("subscribe", None, {"tag": "mytag"}, "")),
        ("subscriptions",
            ("subscriptions", None, {}, "")),

        ("show -t lol --club=fuck",
            ("show", None, {"tag": "lol", "club": "fuck"}, "")),
        ("interface simplified",
            ("interface", "iface", {}, "simplified")),
        ('c "" -am HUX2KJ/2BB',
            ('comment', 'text', {"message": "HUX2KJ/2BB", 'anonymous': True}, "")),
    )

    class ShitMsg(object):
        def __init__(self, b):
            self.body = b
    for t, r in test:
        msg = ShitMsg(t)
        res = p.resolve(msg)[1:]
        print msg, res, r
        assert r == res
    print "Done ok."
else:
    raise Exception("Do not import this shit, just run it!")
