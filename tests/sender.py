#!/usr/bin/env python
# coding: utf-8

import sys
import os.path
sys.path.insert(0, os.path.dirname(__file__))
import time
import random
import datetime
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import xmpp


def get_random_resource():
    rand = "".join(map(lambda _: str(random.randint(0, 9)), xrange(10)))
    return "nyak" + rand


words = [
    u"ня", u"няк", u"нян", u"мявк", u"десу",
    u"хвостоняк", u"пушоняк", u"нявк", u"мурк",
]

imgur_images = [
    "ZLGlB", "CLpz9", "s8KCu", "3TJkV", "57pOq", "gtB2Q", "Q33yJ", "XesYi",
    "SK4NM", "k4pRm", "r9sX3", "f0eGl", "a3tVS", "m7oc6", "KS52w", "qhxtW",
    "ts0Fa", "IQRaf", "tGYNp", "iLmWL", "BLTS1", "Ghvo1", "i9DJk", "VdoPa",
    "h5yAO", "Zfb6P", "ZBNaX", "U44Ro", "uVBxP", "2VzHE", "1Cm4R", "QCv4c",
    "0R6ei", "xwpQ8", "Guioj", "73LEY", "ApB3x", "OO5np", "RLygx", "8P9jV",
    "vGxNh", "q6M5O", "UhUWu", "4olOn", "Z1ago", "zDX6I", "VSuLW", "K6ZcP",
    "k3jsd", "X7CGS", "dgk4G", "Ky03U", "53UFS", "GYvS4", "x9vpy", "QYjFP",
    "m8yfg", "caSDN", "EQ4ze", "29xmF", "jONPp", "7aOM9", "G6Slh", "SwtNR",
]

def get_random_tags():
    rnd = random.random()
    if rnd < 0.5:
        tags_count = 0
    else:
        tags_count = random.randint(1, 4)
    return map(lambda _: "*" + random.choice(words), xrange(tags_count))

def get_random_words():
    word_count = random.randint(3, 10)
    return map(lambda _: random.choice(words).upper(), xrange(word_count))

def get_random_images(images_count=None):
    if images_count is None:
        rnd = random.random()
        if rnd < 0.5:
            images_count = 0
        elif rnd < 0.7:
            images_count = 1
        elif rnd < 0.9:
            images_count = 2
        else:
            images_count = 3
    return map(
        lambda _: "http://imgur.com/" + random.choice(imgur_images),
        xrange(images_count))


def now_s():
    return datetime.datetime.now().strftime("%H:%M:%S.%f")


def message_handler(cl, msg):
    print "[%s] RECV: <<<%s>>>" % (now_s(), msg.getBody())


def send(cl, bnw_jid, args):
    msg = ""
    if args.to:
        msg = args.to + " "
    if not args.msg:
        if not args.no_rnd_tags:
            tags = " ".join(get_random_tags())
            if tags:
                msg += tags + "\n"
        msg += " ".join(get_random_words())
        if not args.no_rnd_imgs:
            imgs = "\n".join(get_random_images(args.imgs_count))
            if imgs:
                msg += "\n" + imgs
    else:
        msg += args.msg
    cl.send(xmpp.Message(to=bnw_jid, typ="chat", body=msg))
    print "[%s] SEND: <<<%s>>>" % (now_s(), msg)


def main(bot_jid, bot_password, bnw_jid, args):
    jid_obj = xmpp.JID(bot_jid)
    if args.verbose:
        kwargs = {}
    else:
        kwargs = {"debug": []}
    cl = xmpp.Client(jid_obj.getDomain(), **kwargs)
    if not cl.connect(use_srv=args.srv):
        sys.stderr.write("Can't connect to server.\n")
        sys.exit(1)
    if not cl.auth(jid_obj.getNode(), bot_password, get_random_resource()):
        sys.stderr.write("Can't auth.\n")
        sys.exit(1)
    cl.RegisterHandler("message", message_handler)
    cl.send(xmpp.Presence(priority="100"))

    if args.count:
        count = 1
    else:
        count = 0
    last_time = datetime.datetime.utcfromtimestamp(0)
    delta = datetime.timedelta(seconds=args.wait)
    try:
        while count <= args.count:
            now = datetime.datetime.now()
            if now - last_time >= delta:
                send(cl, bnw_jid, args)
                last_time = now
                if args.count:
                    count += 1
            cl.Process(0.01)
        # Process remained data.
        while True:
            time.sleep(0.1)
            # Holy crap. Why "0"???
            if cl.Process(0.01) == "0":
                break
    finally:
        cl.sendPresence(typ="unavailable")
        cl.disconnect()


if __name__ == "__main__":
    import argparse
    import config

    parser = argparse.ArgumentParser()
    parser.add_argument("--to", help="destination")
    parser.add_argument("-c", "--count", type=int, default=1,
                        help="how many messages send; 0 for infinity")
    parser.add_argument("-ni", "--no-rnd-imgs", action="store_true",
                        help="no random images")
    parser.add_argument("-ic", "--imgs-count", type=int,
                        help="specified images count")
    parser.add_argument("-nt", "--no-rnd-tags", action="store_true",
                        help="no random tags")
    parser.add_argument("-m", "--msg", help="specified message text")
    parser.add_argument("-w", "--wait", type=float, default=6,
                        help="how many seconds wait before sending new message")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--srv", action="store_true", help="enable SRV lookup")
    args = parser.parse_args(sys.argv[1:])

    main(config.jid, config.password, config.bnw_jid, args)
