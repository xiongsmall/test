import tornado.web
import tornado.httpserver
import tornado.options
import tornado.ioloop

from tornado.options import options, define

define("port", default=8001, help="8001", type=int)

import time

class SleepHandler(tornado.web.RequestHandler):
    def get(self):
        time.sleep(10)
        self.write("this is SleepHandler...")

class DirectHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("this is DirectHandler...")

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r"/d", DirectHandler),
            (r"/s", SleepHandler),
        ],
        debug=False
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.bind(options.port)
    http_server.start(8)
    tornado.ioloop.IOLoop.instance().start()