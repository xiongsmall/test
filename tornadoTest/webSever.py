from multiprocessing import Process
# from exam import app
from socket import *
import re
import sys


class Servernum(object):
    def __init__(self,app,bindnum):
        self.ftp_socket = socket(AF_INET,SOCK_STREAM)
        self.ftp_socket.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        self.ftp_socket.bind(("",bindnum))
        self.ftp_socket.listen(1)
        self.app =app

    def start_reply(self,reply_head):
        self.reply_line = "HTTP/1.1 " + "200 OK" + "\r\n"
        self.reply_head = ""
        for key, value in reply_head:
            self.reply_head += key + value + "\r\n"

    def save_read(self):
        content = self.new_socket.recv(1024).decode("utf-8")
        data = re.search("(/.*)( )",content).group(1)
        dic_data = {"data":data}
        self.reply_data = self.app(dic_data,self.start_reply)
        blankz = "\r\n"
        fin_data = self.reply_line + self.reply_head + blankz + self.reply_data
        self.new_socket.send(fin_data.encode("utf-8"))
        self.new_socket.close()

    def start(self):
        while True:
            self.new_socket,self.new_address = self.ftp_socket.accept()
            Process(target=self.save_read).start()

if __name__ =="__main__":
    pass
    # Servernum()
    # args = sys.argv[1]
    # args1,args2 = args.split(":")
    # m =__import__(args1)
    # app = m.app
    # app = getattr(m,app)
    # Servernum(app,8083).start()