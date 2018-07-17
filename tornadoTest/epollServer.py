# -*-coding:utf-8-*-
from socket import *
import select

ftp_socket = socket(AF_INET,SOCK_STREAM)

ftp_socket.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)

ftp_socket.bind(("",8080))

ftp_socket.listen(0)

epoll =select.epoll()

epoll.register(ftp_socket.fileno(),select.EPOLLIN |select.EPOLLET)

socket_dic = {}
address_dic = {}

while True:
    epoll_list = epoll.poll()
    print(epoll_list)
    for fd,event in epoll_list:
        if fd == ftp_socket.fileno():
            sock,addr = ftp_socket.accept()
            socket_dic[sock.fileno()] = sock
            address_dic[sock.fileno()] = addr
            epoll.register(sock.fileno(),select.EPOLLIN |select.EPOLLET)
        else:
            sock = socket_dic[fd]
            addr = address_dic[fd]
            content = sock.recv(1024)
            if len(content) > 0:
                sock.send(content)
            else:
                print("%s已经下线了")
                sock.close()
                epoll.unregister(fd)
                del socket_dic[fd]
                del address_dic[fd]
ftp_socket.close()
