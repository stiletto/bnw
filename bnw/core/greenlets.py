import gevent

class GreenletMixIn(object):
    def initGreenlets(self):
        self.greenlets = {}
    def spawn(self, f, *a, **kwa):
        gl = gevent.Greenlet(f, *a, **kwa)
        self.greenlets[gl] = {'a': a, 'kwa': kwa}
        gl.link(self.forgetGreenlet)
        gl.start()
        return gl

    def forgetGreenlet(self,gl):
        del self.greentlets[gl]
