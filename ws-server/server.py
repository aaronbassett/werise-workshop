import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
from tornado import gen


class WSHandler(tornado.websocket.WebSocketHandler):

    connections = []

    def open(self):
        self.connections.append(self)

    @gen.coroutine
    def on_close(self):
        # Remove the connection from the list of connections
        self.connections.remove(self)


if __name__ == "__main__":
    application = tornado.web.Application(
        [
            (
                r"/static/(.*)",
                tornado.web.StaticFileHandler,
                {"path": "ws-server/static"},
            ),
            (r"/socket", WSHandler),
        ]
    )

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8801)
    tornado.ioloop.IOLoop.instance().start()
