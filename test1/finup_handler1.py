import gzip,six,time,json,os,imp,pickle,requests,socket
import tornado.web
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor,Future
from tornado import gen
from threading import Lock
lock = Lock()
MODELS = dict()
mod = imp.load_source('toufang__2018060518_model',os.sep.join(['/Users/finup/PycharmProjects/py3/simpleweb/models','toufang__2018060518_model.py']))
# with open('/Users/finup/PycharmProjects/py3/simpleweb/models/toufang__2018060518_model.py','rb') as f:
#     mod = pickle.load(f)

class handler(tornado.web.RequestHandler):
    pro_model = None
    # executor = ThreadPoolExecutor(2)

    @gen.coroutine
    def get(self):
        self.finish(','.join(MODELS.keys()))

    @gen.coroutine
    def post(self):
        print('post in')
        data = self.request.body.strip()
        ret = yield self.process_data(data,mod)
        print(ret)

    # @run_on_executor
    def process_data(self,data,pro_model):
        data = json.loads(data)
        future = Future()
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect(('localhost',8888))
        s.send(b'a')
        def handle_data(sock,event):
            io_loop = tornado.ioloop.IOLoop.current()
            io_loop.remove_handler(sock)
            # aaa = requests.get('http://www.google.com')
            data = sock.recv(1024)
            print(data)
            future.set_result(data)
        aaa = requests.get('http://www.google.com')
        io_loop = tornado.ioloop.IOLoop.current()
        io_loop.add_handler(s,handle_data,io_loop.READ)
        return future

        # lock.acquire()
        # aaa = requests.get('http://www.google.com')
        # data = pro_model.predict_proba(data)
        # lock.release()
        # print(data)


# class LoadModel(object):
#     def load_model(self):
#         models = dict()
#         dirpath = os.path.abspath(os.sep.join([os.getcwd(),'models']))
#         modeldir =os.listdir(dirpath)
#         for mofile in modeldir:
#             fname = mofile.split('.')[0]
#             moname = mofile.split('_model')[0]
#             if mofile.endswith('_model.py'):
#                 mod = imp.load_source(fname,os.sep.join([dirpath, mofile]))
#                 models[moname] = mod
#         self.update(models)
#
#     def update(self,models):
#         global MODELS
#         old_model = MODELS
#         MODELS = models
#         for i in old_model.keys():
#             m = old_model.pop[i,None]
#             if m:
#                 del m
#         del old_model
import tornado.ioloop
import tornado.httpserver
from tornado.options import options, define



define("port", default=8888,help="run server on the given port")


app = tornado.web.Application(
    handlers=[
        (r'/finup', handler),
    ],
    debug=False
)



if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    http_server.start()
    tornado.ioloop.IOLoop.current().start()