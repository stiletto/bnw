import traceback
from uuid import uuid4
import zmq, threading
from twisted.internet import reactor,defer

context = zmq.Context()                  

class ZMQRequestThread(threading.Thread):
    def __init__(self,socket,callback,*args,**kwargs):
        threading.Thread.__init__(self,*args,**kwargs)
        self.socket = socket
        self.callback = callback
        self.running = True
    def run(self):
        while self.running:
            recv = self.socket.recv_multipart()
            self.callback(recv)

class ZMQRequestService(object):
    def __init__(self,connect_addr='tcp://127.0.0.1:7850'):
        self._socket = context.socket(zmq.XREQ)
        self._socket.connect(connect_addr)
        self._started = False
        self.requests = {}
        
    def request(self,request):
        reqid = uuid4().hex
        d = defer.Deferred()
        self.requests[reqid] = d.callback
        self._socket.send_multipart([reqid,request])
        return d

    def start(self):
        if not self._started:
            self._thread = ZMQRequestThread(self._socket,self._callback)
            self._thread.daemon = True
            self._thread.start()
        
    def stop(self):
        if self._started:
            self._thread.running = False
            self._thread.stop()
            self.requests = {}

    def _callback(self,recv):
        try:
            reactor.callFromThread(self.requests[recv[0]],recv[2])
            del self.requests[recv[0]]
        except:
            print 'ICB',traceback.format_exc()

