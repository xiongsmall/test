import tornado.ioloop as loop
from tornado.options import options,define
from tornado import gen
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor
import tornado.web as web,tornado.httpserver as http
import time
from concurrent.futures import ThreadPoolExecutor
# thread_pool = ThreadPoolExecutor(5)



define("port",default=8380,help='run 8380',type=int)


class MainHandler(web.RequestHandler):
    executor = ThreadPoolExecutor(20)

    @gen.coroutine
    def get(self):
        # yield self.workfun()
        self.workfun()
    @gen.coroutine
    def post(self):
        pass

    @run_on_executor
    # @gen.coroutine
    def workfun(self):
        # self.write('aaaaeqwmk lkqmlwq')
        time.sleep(0.03)
    #
    # # @gen.coroutine
    # def mysleep(self,count):
    #     for i in range(count):
    #         time.sleep(1)
    # def work_fun(self):
        # time.sleep(0.5)
    #     self.write('aaaa')
    # @gen.coroutine
    # def get(self):
    #     yield self.work_fun()

        # time1 = time.time()
        # print(111,time1)
        # yield self.mysleep(5)
        # yield thread_pool.submit(self.mysleep,5)
        # time2 = time.time()
        # print(222,time2)

        # print('time:%s'%(time2-time1))


app= web.Application([(r'/',MainHandler)]
                     # ,debug=True
                     )
if __name__ == "__main__":
    apps = http.HTTPServer(app)
    apps.bind(options.port)
    apps.start(0)
    loop.IOLoop.instance().start()