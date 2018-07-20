import socket,select,os,Queue,traceback,time,sys,re
# from socket import socket,AF_INET,SOCK_STREAM,SOL_SOCKET,SO_REUSEADDR


class Myserver(object):
    __instance = None

    def __init__(self):
        self.event = None
        self.client  = {}
        self.servers = {}

    @staticmethod
    def newcls():
       if Myserver.__instance == None:
           Myserver.__instance = Myserver()
       return Myserver.__instance



    def startSrv(self,ip,port):
        server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server.setblocking(False)
        server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        server.bind((ip,port))
        server.listen(100)
        serverinfo = Newserver()
        serverinfo.obj = server
        srvId = len(self.servers)
        self.servers[srvId] = serverinfo
        return srvId

    def senddata(self,sock,package):
        sock.send(package)
        self.client.pop(sock.fileno())
        self.event.delFdEvent(sock.fileno(),1|2)
        sock.close()

    def setpro(self,srvId,processor):
        if self.servers.has_key(srvId):
            serverInfo = self.servers[srvId]
            serverInfo.onRead = processor.onRead
            # serverInfo.onconn = processor.onConn
            # serverInfo.onClose = processor.onClose
            return 0
        else:
            return -1

    def start(self):
        if self.event is None:
            self.event = Newevent()
        for srvId,server in self.servers.iteritems():
            self.event.addfdevent(server.obj.fileno(),1,self.onAccept,srvId)
        return self.event.run()


    def onAccept(self,fd,data):
        serverInfo = self.servers[data]
        # try:
        client = CClient()
        client.srvId =data
        client.obj,client.addr = serverInfo.obj.accept()
        self.client[client.obj.fileno()] = client
        client.obj.setblocking(False)
        client.obj.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
        self.event.addfdevent(client.obj.fileno(),1,self.onTcpRead,client)

    def onTcpRead(self,fd, data):
        clientInfo = self.client[fd]
        serverInfo = self.servers[clientInfo.srvId]

        try:
            inBuf = clientInfo.obj.recv(8192)

            if len(inBuf) == 0:
                self.close(clientInfo.obj)
                return

            elif len(inBuf) > 0:
                clientInfo.inBuf += inBuf
                while True:
                    package = clientInfo.inBuf
                    sock = clientInfo.obj
                    serverInfo.onRead(sock, package)
                    break
            else:
                self.close(clientInfo.obj)
        except IOError:
            traceback.print_exc()
            self.close(clientInfo.obj)
                    # serverInfo.onError('onTcpRead io exception')
        except:
            traceback.print_exc()

    def close(self):
         pass


class CClient(object):
    def __init__(self):
        self.srvId = 0
        self.obj = None
        self.addr = None
        self.needClose = False
        self.inBuf = ''
        self.outBuf = ''


class Newserver(object):
    def __init__(self):
        self.obj = None
        self.onRead = None
        self.onClose = None
        self.ip = ''
        self.port = 0


class Newevent(object):
    def __init__(self):
        self.epollhand = select.epoll()
        self.fd = {}
        self.runFlag = True
        self.timeHeap = []
        self.runflag = True
        self.pipe = os.pipe()
        self.MsgQueue = Queue.Queue(1000)
        self.addfdevent(self.pipe[0],1,None,None)


    def addfdevent(self,fd,mask,callback,data):
        ctrl = False
        if self.fd.has_key(fd):
            ctrl = True
        event = self.fd.setdefault(fd, EventData())
        event.mask = event.mask | mask
        evMask = event.mask
        if mask & 1:
            event.onRead = callback
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
            self.epollhand.modify(fd, epollmask)
        else:
            self.epollhand.register(fd, epollmask)
        return True


    def run(self):
        while self.runFlag:
            try:
                epollEvents = self.epollhand.poll()
                for epollEvent in epollEvents:
                    if epollEvent[1] & select.EPOLLIN or epollEvent[1] & select.EPOLLERR or epollEvent[1] & select.EPOLLHUP:
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


    def delFdEvent(self,fd,mask):
        if self.fd.has_key(fd):
            event = self.fd[fd]
            event.mask = event.mask & (~mask)
            evMask = event.mask
            epollMask = 0
            if evMask & 1:
                epollMask |= 1
            if evMask & 2:
                epollMask |= 2
            if event.mask == 0:
                self.fd.pop(fd)
                self.epollhand.unregister(fd)
            else:
                self.epollhand.modify(fd,epollMask)

class EventData(object):
    def __init__(self):
        self.rdata = None
        self.wdata = None
        self.onRead = None
        self.onWrite = None
        self.mask = 0


class WebServer(Myserver):
    instance = None

    @staticmethod
    def newcls():
        if WebServer.instance == None:
            WebServer.instance = WebServer()
        return WebServer.instance

    def onRead(self, sock, package):
        print(package)
        data = re.search(r'\n\n([\s\S]*)', package)
        print(data.group(1))
        # Myserver.newcls().senddata(sock,data1)
        pass


if __name__ == '__main__':
    # LoadModel().load_model()
    srverid = Myserver.newcls().startSrv('0.0.0.0',9999)
    Myserver.newcls().setpro(srverid,WebServer.newcls())
    Myserver.newcls().start()