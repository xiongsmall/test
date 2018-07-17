#!/usr/bin/env python
# -*- coding:utf-8 -*-

import tornado
from tornado.options import define,options
from tornado.escape import json_decode
import tornado.web
import json
import pickle
import tornado.options
import sys
from tornado import gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
import time

define("port", default=8888, help="run on the given port", type=int)
define("cpu", default=1, help="run on the given cpu", type=int)

with open('./getui_loan_2018052215.pkl','rb') as f:
    print("load model")
    model=pickle.load(f)

class IndexHandler(tornado.web.RequestHandler):

    executor = ThreadPoolExecutor(16)

    @gen.coroutine
    def get(self):
        print(self.request)
        self.write('hello world!')

    @gen.coroutine
    def post(self):
        t = time.time()
        if len(self.request.files.get('file',[])) > 0:
            data_origin = self.request.files["file"][0].pop("body").strip()
        else:
            data_origin = self.request.body.strip()
        print(data_origin)
        out = yield self.sleep(data_origin)
        #in_data=json.loads(data_origin)[0]
        #out=model.predict_proba([in_data[-1]])[0][1]
        time_elapsed = time.time() - t
        print("process time",time_elapsed)
        self.write(str(out))

    @run_on_executor
    def sleep(self, data_origin):
        print(data_origin)
        in_data=json.loads(data_origin)[0]
        out=model.predict_proba([in_data[-1]])[0][1]
        print(out)
        return out

if __name__=='__main__':
    import tornado.httpserver,tornado.ioloop
    tornado.options.parse_command_line()
    app=tornado.web.Application(handlers=[(r'/',IndexHandler)])
    http_server=tornado.httpserver.HTTPServer(app)
    http_server.bind(options.port)
    http_server.start(1)
    tornado.ioloop.IOLoop.instance().start()
