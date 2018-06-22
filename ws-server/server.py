import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web


if __name__ == "__main__":
    application = tornado.web.Application(
        [(r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "ws-server/static"})]
    )

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8801)
    tornado.ioloop.IOLoop.instance().start()
