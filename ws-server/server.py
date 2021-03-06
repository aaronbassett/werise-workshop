import os
import requests
import json
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
from tornado import gen
from watson_developer_cloud import ToneAnalyzerV3


class DashboardUIHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/dashboard.html", server_url=os.environ["TORNADO_WS_URL"])


class DashboardHandler(tornado.websocket.WebSocketHandler):

    connected_clients = set()

    def check_origin(self, origin):
        return True

    def open(self):
        DashboardHandler.connected_clients.add(self)

    def on_close(self):
        DashboardHandler.connected_clients.remove(self)

    @classmethod
    def send_updates(cls, tones):
        for connected_client in cls.connected_clients:
            connected_client.write_message(tones)


class WSHandler(tornado.websocket.WebSocketHandler):

    connections = []

    def initialize(self, **kwargs):
        self.transcriber = tornado.websocket.websocket_connect(
            f"wss://stream.watsonplatform.net/speech-to-text/api/v1/recognize?watson-token={self.transcriber_token}&model=en-UK_NarrowbandModel",
            on_message_callback=self.on_transcriber_message,
        )

        self.tone_analyzer = ToneAnalyzerV3(
            username=os.environ["WATSON_TONE_ANALYZER_USERNAME"],
            password=os.environ["WATSON_TONE_ANALYZER_PASSWORD"],
            version="2016-05-19",
        )

    @property
    def transcriber_token(self):
        resp = requests.get(
            "https://stream.watsonplatform.net/authorization/api/v1/token",
            auth=(
                os.environ["WATSON_TRANSCRIPTION_USERNAME"],
                os.environ["WATSON_TRANSCRIPTION_PASSWORD"],
            ),
            params={"url": "https://stream.watsonplatform.net/speech-to-text/api"},
        )
        return resp.content.decode("utf-8")

    @gen.coroutine
    def on_message(self, message):
        transcriber = yield self.transcriber

        if type(message) != str:
            transcriber.write_message(message, binary=True)
        else:
            data = json.loads(message)
            data["action"] = "start"
            data["continuous"] = True
            data["interim_results"] = True
            transcriber.write_message(json.dumps(data), binary=False)

    def on_transcriber_message(self, message):
        if message:
            message = json.loads(message)
            if "results" in message:
                transcript = message["results"][0]["alternatives"][0]["transcript"]
                tone_results = self.tone_analyzer.tone(
                    tone_input=transcript, content_type="text/plain"
                )
                tones = tone_results["document_tone"]["tone_categories"][0]["tones"]

                DashboardHandler.send_updates(json.dumps(tones))

    def open(self):
        self.connections.append(self)

    @gen.coroutine
    def on_close(self):
        # Remove the connection from the list of connections
        self.connections.remove(self)
        transcriber = yield self.transcriber
        data = {"action": "stop"}
        transcriber.write_message(json.dumps(data), binary=False)
        transcriber.close()


if __name__ == "__main__":
    application = tornado.web.Application(
        [
            (
                r"/static/(.*)",
                tornado.web.StaticFileHandler,
                {"path": "ws-server/static"},
            ),
            (r"/socket", WSHandler),
            (r"/dashboard-socket", DashboardHandler),
            (r"/dashboard", DashboardUIHandler),
        ]
    )

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8801)
    tornado.ioloop.IOLoop.instance().start()
