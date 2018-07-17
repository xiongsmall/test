from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado import gen,web
from time import sleep
from tornado.options import options, define
from concurrent.futures import ThreadPoolExecutor
from tornado.ioloop import IOLoop
from tornado.concurrent import run_on_executor
from tornado.web import RequestHandler, Application, authenticated

define("port", default=8080,help="run server on the given port")

class MainHandler(RequestHandler):
    executor = ThreadPoolExecutor(2)
    def get(self):
        # self.aa()
        self.write("aaaaa")

    @web.asynchronous
    @gen.coroutine
    def post(self):
        time= self.get_argument('time',None)
        yield self.aa(time)
        print('aaa')

    @run_on_executor
    def aa(self,time):
        time = int(time)
        sleep(time)
        print('bbb')


app =Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    options.parse_command_line()
    http_server =HTTPServer(app)
    http_server.bind(options.port)
    http_server.start()
    # http_server.listen(options.port)
    IOLoop.current().start()