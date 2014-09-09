import random
from base import *
from bnw.core.base import config
import bnw.core.bnw_objects as objs
from bnw.handlers import command_post


class SimpleSetting(object):
    def __init__(self, default=None):
        self.default = default

    def get(self, request, name):
        setts = request.user.get('settings', {})
        return setts.get(name, self.default)

    @defer.inlineCallbacks
    def write(self, request, name, value):
        if len(value) > 2048:
            defer.returnValue((False, ('%s value is too long.' % (name,))))
        _ = yield objs.User.mupdate({'name': request.user['name']},
                                    {'$set': {'settings.' + name: value}})
        defer.returnValue((True,))

class BooleanSetting(object):
    def __init__(self, default=False):
        self.default = default

    def get(self, request, name):
        setts = request.user.get('settings', {})
        return setts.get(name, self.default)

    @defer.inlineCallbacks
    def write(self, request, name, value):
        value_lowercase = value.lower()
        if value_lowercase in ('on', 'yes', 'true', 't', 'y', '1'):
            new_value = True
        elif value_lowercase in ('off', 'no', 'false', 'f', 'n', '0'):
            new_value = False
        else:
            defer.returnValue((False, ('Unable to parse %s value. Try to use "yes"/"no" (or "on"/"off").' % (name,))))
        _ = yield objs.User.mupdate({'name': request.user['name']},
                                    {'$set': {'settings.' + name: new_value}})
        defer.returnValue((True,))


class ServiceJidSetting(SimpleSetting):
    def get(self, request, name):
        setts = request.user.get('settings', {})
        return setts.get(name, config.srvc_name)

    def write(self, request, name, value):
        return SimpleSetting.write(self, request, name, request.to.userhost())

optionnames = {
    'usercss': SimpleSetting(),
    'notify_on_recommendation': BooleanSetting(True),
    'password': SimpleSetting(),
    'servicejid': ServiceJidSetting(),
    'baseurl': SimpleSetting(),
    'about': SimpleSetting(),
    'default_format': SimpleSetting(),
}


@require_auth
@defer.inlineCallbacks
def cmd_set(request, **kwargs):
    if not kwargs:
        # Show current settings.
        current = {}
        for n, v in optionnames.iteritems():
            current[n] = v.get(request, n)
        defer.returnValue(
            dict(ok=True, format='settings', settings=current))
    else:
        if 'name' in kwargs:
            # Simplified interface.
            name, value = kwargs['name'], kwargs['value']
            if value is None:
                value = ''
        else:
            # Redeye interface.
            name, value = kwargs.items()[0]
        if not name in optionnames:
            defer.returnValue(
                dict(ok=False, desc='Unknown setting: %s' % kwargs['name']))
        else:
            if name is 'default_format':
                if not value in command_post.acceptable_formats:
                    defer.returnValue(dict(ok=False, desc=u"'%s' is not a valid format! Choose one of: %s" % (value, command_post.acceptable_formats_str)))
                else:
                    value = command_post.normalize_format(value)
            res = yield optionnames[name].write(request, name, value)
            if not res[0]:
                defer.returnValue(
                    dict(ok=False, desc=res[1])
                )
        defer.returnValue(
            dict(ok=True, desc='Settings updated.'))
