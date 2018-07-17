import socket,select,os,Queue,traceback,time,heapq,time
from socket import socket,AF_INET,SOCK_STREAM,SOL_SOCKET,SO_REUSEADDR
class Newserver(object):
    def __init__(self):
        self.obj = None
        self.onRead = None
        self.onConn = None
        self.onClose = None
        self.onError = None
        self.ip = ''
        self.port = 0

class Myserver(object):
    def __init__(self):
        self.event = None
        self.client  = {}
        self.servers = {}
        self.times = {}

    def startSrv(self,ip,port):
        server = socket(AF_INET,SOCK_STREAM)
        # server.setblocking(False)
        server.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        server.bind((ip,port))
        server.listen(1024)
        serverinfo = Newserver()
        serverinfo.obj = server
        srvId = len(self.servers)
        self.servers[srvId] = serverinfo
        return srvId

    def setpro(self,srvId,processor):
        if self.servers.has_key(srvId):
            serverInfo = self.servers[srvId]
            serverInfo.onRead = processor.onRead
            serverInfo.onconn = processor.onConn
            serverInfo.onClose = processor.onClose
            serverInfo.onError = processor.onError
            return 0
        else:
            return -1

    def start(self):
        if self.event is None:
            self.event = Newevent()
        for srvId,server in self.servers.iteritems():
          self.event.addfdevent(server.obj.fileno(),1,self.onAccept,srvId)

    def onAccept(self,fd,data):
        serverInfo = self.servers[data]
        try:
            client = CClient()
            client.srvId =data
            client.obj,client.addr = serverInfo.obj.accept()
            self.client[client.obj.fileno()] = client
            client.obj.setblocking(False)
            client.obj.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

            session = CSession()
            session.obj = client.obj
            session.addr = client.addr
            session.srvId = data
            self.event.addfdevent(client.obj.fileno(),1,self.onTcpRead,client)
            serverInfo.onconn(session,True)
        except socket.error,e:
            errno,errmsg = e
            if errno != 11:
                serverInfo.onError('onAccept'+errmsg)

    def onTcpRead(self, fd, data):

        clientInfo = self.client[fd]
        serverInfo = self.servers[clientInfo.srvId]

        try:
            inBuf = clientInfo.obj.recv(8192)

            if len(inBuf) == 0:
                session = CSession()
                session.srvId = clientInfo.srvId
                session.obj = clientInfo.obj
                session.addr = clientInfo.addr
                serverInfo.onClose(session)
                self.close(clientInfo.obj)
                return

            elif len(inBuf) > 0:
                clientInfo.inBuf += inBuf
                while True:
                    packLen = serverInfo.filter.isWholePackage(clientInfo.inBuf)
                    if packLen > 0:
                        session = CSession()
                        session.srvId = clientInfo.srvId
                        session.obj = clientInfo.obj
                        session.addr = clientInfo.addr

                        package = clientInfo.inBuf[0:packLen]

                        clientInfo.inBuf = clientInfo.inBuf[packLen:len(clientInfo.inBuf)]
                        serverInfo.onRead(session, package)
                    elif packLen == 0:
                        # package not ready
                        break
                    elif packLen == -1:
                        # package invalid
                        self.close(clientInfo.obj)
                        serverInfo.onError('onTcpRead invalid package')

            else:
                self.close(clientInfo.obj)
                serverInfo.onError('onTcpRead recv data error')
        except IOError:
            traceback.print_exc()
            self.close(clientInfo.obj)
            serverInfo.onError('onTcpRead io exception')
        except:
            traceback.print_exc()
            serverInfo.onError('onTcpRead exception')

    def fork(self, num):
        exit = 0
        for i in range(num):
            pid = os.fork()
            if pid > 0:
                if i == (num - 1):
                    while 1:
                        info = os.wait()
                        print 'process', info[0], "exit"
                        exit += 1
                        if exit == num:
                            break

            else:
                self.startser()

    def startser(self):
        if self.event is None:
            self.event = Newevent()
        for srvId, server in self.servers.iteritems():
            pass
            self.event.addfdevent(server.obj.fileno(), 1, self.onAccept, srvId)
        # for timer in self.times.itervalues():
        #     pass
        #     self.event.addTimer(timer[0], timer[1], timer[2], timer[3])
        return self.event.run()



    def close(self, sock):

        self.client.pop(sock.fileno())
        self.event.delFdEvent(sock.fileno(), 1 | 2)
        sock.close()




class Newevent(object):
    def __init__(self):
        self.epollhand = select.epoll()
        self.fd = {}
        self.runFlag = True
        self.timeHeap = []
        self.runflag = True
        self.pipe = os.pipe()
        self.MsgQueue = Queue.Queue(10000)
        self.addfdevent(self.pipe[0],1,None,None)

    def addfdevent(self,fd,mask,callback,data):
        ctrl = False
        if self.fd.has_key(fd):
            ctrl = True
        event = self.fd.setdefault(fd,CEventData())
        event.mask = event.mask | mask
        evMask = event.mask

        if mask & 1:
            event.onread = callback
            event.rdata = data
        if mask & 2:
            event.onWrite = callback
            event.wdata = data
        epollmask = 0
        if evMask & 1:
            epollmask |= select.EPOLLIN
        if evMask & 2:
            epollmask |= select.EPOLLOUT

        if ctrl:
            self.epollhand.modify(fd,epollmask)
        else:
            self.epollhand.register(fd,epollmask)
        return True

    def run(self):
        while self.runFlag:
            try:
                timeNow =(int(time.time() * 1000))
                expire = 1
                while True:
                    if len(self.timeHeap) == 0:
                        break
                    timer = heapq.nsmallest(1, self.timeHeap)[0]

                    if timer[0] <= timeNow:
                        self.timeHeap.remove(timer)
                        self.timeHeap.pop(timer[1])

                        if timer[2]:
                            timer[2](timer[1], timer[3])
                    else:
                        break

                epollEvents = self.epollhand.poll(expire)

                for epollEvent in epollEvents:
                    if epollEvent[1] & select.EPOLLIN or epollEvent[1] & select.EPOLLERR or epollEvent[
                        1] & select.EPOLLHUP:

                        # for event message
                        if epollEvent[0] == self.pipe[0]:

                            os.read(epollEvent[0], 1)
                            callable, args, kwds = self.MsgQueue.get_nowait()
                            callable(*args, **kwds)
                            self.MsgQueue.task_done()

                        else:
                            if self.fd[epollEvent[0]].onRead:
                                self.fd[epollEvent[0]].onRead(epollEvent[0], self.fd[epollEvent[0]].rdata)

                    if (epollEvent[1] & select.EPOLLOUT):
                        if self.fd[epollEvent[0]].onWrite:
                            self.fd[epollEvent[0]].onWrite(epollEvent[0], self.fd[epollEvent[0]].wdata)
            except Exception as e:
                traceback.print_exc()
                continue


class CEventData(object):
    def __init__(self):
        self.rdata = None
        self.wdata = None
        self.onRead = None
        self.onWrite = None
        self.mask = 0


class CClient(object):
    def __init__(self):
        self.srvId = 0
        self.obj = None
        self.addr = None
        self.needClose = False
        self.inBuf = ''
        self.outBuf = ''

class CSession(object):
    def __init__(self):
        self.srvId = 0
        self.obj = None
        self.addr = None
        self.cTime = int(time.time())

class WebServer(Myserver):
    pass

if __name__ == '__main__':
    srverid = Myserver().startSrv('0.0.0.0',9999)
    WebServer().__init__()
    Myserver().setpro(srverid,WebServer())
    Myserver().start()
    Myserver().fork(4)