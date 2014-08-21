# -*- coding: utf-8 -*-

from base import *
import time
import pymongo.errors
from bnw.core.base import config
import bnw.core.bnw_objects as objs
from twisted.python import log

@defer.inlineCallbacks
def check_interval(job_name, interval):
    now = time.time()
    name = 'last_' + job_name
    try:
        upresult = yield objs.GlobalState.mupdate(
            {'name': name, 'value': {'$lt': now-interval}},
            {'name': name, 'value': now}, upsert=True, w=1)
    except pymongo.errors.DuplicateKeyError:
        return False
    return upresult['n'] > 0

@defer.inlineCallbacks
def do_mapreduce():
    now = time.time()
    if yield check_interval('clubs', 6*3600):
        yield objs.Message.map_reduce(
            map='function() { this.clubs.forEach(function(z) { emit(z, 1);}); }',
            reduce='function(k,vals) { var sum=0; for(var i in vals) sum += vals[i]; return sum; }',
            out={'replace': objs.Club.collection.collection_name}) # do not hardcode collection names

    if yield check_interval('tags', 6*3600):
        yield objs.Message.map_reduce(
            map='function() { this.tags.forEach(function(z) { emit(z, 1);}); }'
            reduce='function(k,vals) { var sum=0; for(var i in vals) sum += vals[i]; return sum; }',
            out={'replace': objs.Tag.collection.collection_name})

    if yield check_interval('today', 300):
        start = now - 86400
        yield objs.Comment.map_reduce(
            map='function() { emit(this.message, 1); }'
            reduce='function(k,vals) { var sum=0; for(var i in vals) sum += vals[i]; return sum; }'
            query={'date': {'$gte': start}}
            out={'replace': objs.Today.collection.collection_name})

    if yield check_interval('usertags', 86400):
        yield objs.Message.map_reduce(
            map='''function () {
                var user = this.user;
                for (var i in this.tags) {
                    var tag = this.tags[i];
                    emit(user+" "+tag, {count:1, tag: tag, user: user});
                }
            }'''
            reduce='''function (k, vals) {
                var sum = 0;
                var user;
                var tag;
                for (var i in vals) {
                    var val = vals[i];
                    sum += val.count;
                    if (i==0) {
                        tag = val.tag;
                        user = val.user;
                    }
                }
                return {count:sum, tag:tag, user:user};
            ''',
            out={'replace': objs.UserTag.collection.collection_name})
        yield objs.UserTag.ensure_indexes()

@defer.inlineCallbacks
def map_reduce_timer():
    try:
        yield do_mapredue()
    except:
        log.msg('MapReduce failed: %s ' % (traceback.format_exc(),))
    reactor.callLater(300, map_reduce_timer)
    defer.returnValue(None)

def setup_mapreduce():
    if config.mapreduce_enabled:
        reactor.callLater(300, map_reduce_timer)
