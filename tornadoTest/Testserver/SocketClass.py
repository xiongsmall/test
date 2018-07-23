# coding: utf-8
import socket,select,os,Queue,traceback,sys,imp,re
from socket import socket,AF_INET,SOCK_STREAM,SOL_SOCKET,SO_REUSEADDR
from threading import Thread

reload(sys)
sys.setdefaultencoding('utf-8')

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
    instance = None
    def __init__(self):
        self.event = None
        self.client  = {}
        self.servers = {}
        self.times = {}

    def senddata(self,sock,ret):
        sock.sendall(ret)
        self.client.pop(sock.fileno())
        self.event.delFdEvent(sock.fileno(),1|2)
        sock.close()
    @staticmethod
    def newcls():
       if Myserver.instance == None:
           Myserver.instance = Myserver()
       return Myserver.instance


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

    def getdata(self,package):
        datalines = package.splitlines()
        Index = None
        for index, str in enumerate(datalines):
            if not str:
                Index = index
        dataline = datalines[Index + 1:]
        data = ''.join(dataline)
        return eval(data)
        # if type(data) == list:
        #     return eval(data)
        # else:
        #     return data

    def runmodel(self,model,data):
        self.pro_model = MODELS[model]
        predict_proda = self.pro_model.predict_proba
        ret = predict_proda(data)
        return ret


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
        client = CClient()
        client.srvId =data
        client.obj,client.addr = serverInfo.obj.accept()
        self.client[client.obj.fileno()] = client
        client.obj.setblocking(False)
        client.obj.setsockopt(SOL_SOCKET,SO_REUSEADDR, 1)
        self.event.addfdevent(client.obj.fileno(),1,self.onTcpRead,client)


    def onTcpRead(self, fd, data):
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
                    serverInfo.onRead(sock,package)
                    break
            else:
                self.close(clientInfo.obj)
        except IOError:
            traceback.print_exc()
            self.close(clientInfo.obj)
        except:
            traceback.print_exc()

    def fork(self, num):
        exit = 0
        for i in range(num):
            pid = os.fork()
            if pid > 0:
                if i == (num - 1):
                    while 1:
                        info = os.wait()
                        exit += 1
                        if exit == num:
                            break
            else:
                self.startser()

    def startser(self):
        if self.event is None:
            self.event = Newevent()
        for srvId, server in self.servers.iteritems():
            self.event.addfdevent(server.obj.fileno(), 1, self.onAccept, srvId)
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
            self.epollhand.modify(fd,epollmask)
        else:
            self.epollhand.register(fd,epollmask)
        return True


    def run(self):
        while self.runFlag:
            try:
                epollEvents = self.epollhand.poll(1)
                print(epollEvents)
                for epollEvent in epollEvents:
                    if epollEvent[1] & select.EPOLLIN or epollEvent[1] & select.EPOLLERR or epollEvent[1] & select.EPOLLHUP:
                        if epollEvent[0] == self.pipe[0]:
                            os.read(epollEvent[0], 1)
                            callable, args, kwds = self.MsgQueue.get_nowait()
                            callable(*args, **kwds)
                            self.MsgQueue.task_done()
                        else:
                            if self.fd[epollEvent[0]].onRead:
                                # Thread(target=self.fd[epollEvent[0]].onRead,args=(epollEvent[0], self.fd[epollEvent[0]].rdata)).start()
                                # print(self.fd[epollEvent[0]].onRead)
                                # time.sleep(2)
                                self.fd[epollEvent[0]].onRead(epollEvent[0], self.fd[epollEvent[0]].rdata)
                    if (epollEvent[1] & select.EPOLLOUT):
                        if self.fd[epollEvent[0]].onWrite:
                            self.fd[epollEvent[0]].onWrite(epollEvent[0], self.fd[epollEvent[0]].wdata)
            except Exception as e:
                print(e)
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

class CSession(object):
    def __init__(self):
        self.srvId = 0
        self.obj = None
        self.addr = None

class WebServer(Myserver):
    instance = None
    @staticmethod
    def newcls():
       if WebServer.instance == None:
           WebServer.instance = WebServer()
       return WebServer.instance

    def onRead(self,sock,package):
        method = re.match(r'(\w*)\s(/\w*)',package)
        if method.group(1) == 'POST':
            model = re.search(r'model=(.*)? ',package).group(1)
            if model in MODELS.keys():
                data = self.getdata(package)
                # data = [[0.966780, '0', '1', '6', '湖北省', '武汉', 7.0, 0.0, 0.0, 0, 0, 5],
                #  [0.966780, '0', '1', '6', '湖北省', '武汉', 7.0, 0.0, 0.0, 0, 0, 5],
                #  [0.966780, '0', '1', '6', '湖北省', '武汉', 7.0, 0.0, 0.0, 1, 0, 5]]
                ret = self.runmodel(model,data)
                print(ret)
                Myserver.newcls().senddata(sock, '1')
            else:
                sock.close()
            # data = re.search(r'\n\n([\s\S]*)',package,re.S).group(1)
        elif method.group(1) == 'GET':
            pass
            # Myserver.newcls().senddata(sock,'1')

    # def onError(self):
    #     print('eeeee')
    #     pass


MODELS = dict()
class LoadModel(object):
    def load_model(self):
        models = dict()
        dirpath = os.path.abspath(os.sep.join([os.getcwd(),'models']))
        modeldir =os.listdir(dirpath)
        for mofile in modeldir:
            fname = mofile.split('.')[0]
            moname = mofile.split('_model')[0]
            if mofile.endswith('_model.py'):
                mod = imp.load_source(fname,os.sep.join([dirpath, mofile]))
                models[moname] = mod
        self.update(models)

    def update(self,models):
        global MODELS
        old_model = MODELS
        MODELS = models
        for i in old_model.keys():
            m = old_model.pop[i,None]
            if m:
                del m
        del old_model

if __name__ == '__main__':
    LoadModel().load_model()
    srverid = Myserver.newcls().startSrv('0.0.0.0',9998)
    Myserver.newcls().setpro(srverid,WebServer.newcls())
    # Myserver.newcls().start()
    Myserver.newcls().fork(4)

