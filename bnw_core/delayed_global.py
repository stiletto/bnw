# coding: utf-8

class DelayedNonexistent(object):
    def __init__(self,name=None):
        self.name = name
    def __getattribute__(self,name):
        raise AttributeError('Attempted to use empty DelayedGlobal "%s" (attribute "%s")' % 
            (super(DelayedNonexistent,self).__getattribute__('name'),name))

class DelayedGlobal(object):
    def __init__(self,name=None):
        self.real = DelayedNonexistent(name)
        pass
    def __getattribute__(self,name):
        if name!='register':
            return getattr(super(DelayedGlobal,self).__getattribute__('real'),name)
        else:
            return super(DelayedGlobal,self).__getattribute__(name)
    def register(self,real):
        self.real = real
