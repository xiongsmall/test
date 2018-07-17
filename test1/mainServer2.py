# coding:utf-8
import tornado.web,tornado.ioloop
import tornado.httpserver
from tornado.options import options, define
from simpleweb import finup_handler


define("port", default=8888,help="run server on the given port")


app = tornado.web.Application(
    handlers=[
        (r'/finup', finup_handler.handler),
    ],
    debug=False
)

if __name__ == "__main__":
    finup_handler.LoadModel().load_model()
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.bind(options.port)
    http_server.start(1)
    tornado.ioloop.IOLoop.current().start()
