# -*-coding:utf-8-*-
from multiprocessing import Process
from socket import *
import re

def test1(new_socket,new_address):
    # new_socket.settimeout(5)
    count = new_socket.recv(1024)
    print(len(count))
    # if len(count) >0:
        # print(count.decode("gb2312"))
    try:
        resquest = count.decode("utf-8")
        ccc = resquest.splitlines()[0]
        ddd = re.search(r"(/.*)(\s)", ccc)
        path = ddd.group(1)
    except:
        path = ''

    if path =="/":
        path ="xiongxiong"

    try:
        d = open("./"+path,"r").read()
    except Exception as e:
        a = "HTTP/1.1 404 NO\r\n"
        b = "Bdqid: 0xe6635f9900016178\r\n"
        c = "\r\n"
        d ="aaaaa"
    else:
        # data = f.read()
        # f.close()
        a = "HTTP/1.1 200 OK\r\n"
        b = "Bdqid: 0xe6635f9900016178\r\n"
        c = "\r\n"
        d = 'bbbbbb'
        # d = data.decode("utf-8")
    e = a + b + c + d
    new_socket.send(e.encode("utf-8"))
    new_socket.close()

if __name__ == '__main__':
    tcp_socket = socket(AF_INET,SOCK_STREAM)
    tcp_socket.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    tcp_socket.bind(("",8088))
    tcp_socket.listen(10)
    try:
        while True:
            new_socket,new_address = tcp_socket.accept()
            t1 = Process(target=test1,args=(new_socket,new_address))
            t1.start()
            new_socket.close()
    except Exception as e:
        print(e)
    finally:
        tcp_socket.close()
