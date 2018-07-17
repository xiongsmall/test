import sys
print('aaa')
sys.stdout.flush()
line = sys.stdin.readline().strip()
print(line)
print('ccc')

import socket,traceback,os

def reap():
    while 1:
        try:
            result = os.waitpid(-1,os.WNOHANG)
            if not result[0]: break
        except:
            break
        print('reaped child process %d'%result[0])

host = ''
port = 51423

if __name__ =='__main__':
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    s.bind((host,port))
    s.listen(1)
    while True:
        try:
            clientsock,clientaddr = s.accept()
        except KeyboardInterrupt:
            raise
        except:
            traceback.print_exc()
            continue
        reap()
        pid = os.fork()
        if pid:
            clientsock.close()
            continue
        else:
            s.close()

        try:
            print('child from %s being handled by PID%d'%(clientsock.getpeername(),os.getpid()))
            while True:
                data = clientsock.recv(4069)
                if not len(data):
                    break
                clientsock.sendall(data)
        except (KeyboardInterrupt,SystemExit):
            raise
        except:
            traceback.print_exc()

        try:
            clientsock.close()
        except KeyboardInterrupt:
            raise
        except:
            traceback.print_exc()
        sys.exit(0)