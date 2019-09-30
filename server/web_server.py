import os

from pathlib import Path

from twisted.web import server, resource, static, http
from twisted.internet import reactor

from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol
from autobahn.twisted.resource import WebSocketResource

import utils.helper as helper

script_path = Path(os.path.dirname(__file__))
project_root_path = script_path.parent


class MyServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {}".format(request.peer))

    def connectionLost(self, reason):
        print("Client disconnected")

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {} bytes".format(len(payload)))
        else:
            print("Text message received: {}".format(payload.decode('utf8')))

        ## echo back message verbatim
        self.sendMessage(payload, isBinary)


if __name__ == "__main__":

    port = 8000

    # web server
    root = resource.Resource()

    rootPage = static.File(os.path.join(project_root_path,"client/index.html"))
    root.putChild(helper.str_to_utf8(''), rootPage)

    client_path = os.path.join(project_root_path, "client/")
    for file in os.listdir(client_path):
            root.putChild(helper.str_to_utf8(file), static.File(client_path + file))

    site = server.Site(root)

    # websocket / tcp
    factory = WebSocketServerFactory()
    factory.protocol = MyServerProtocol
    ws_resource = WebSocketResource(factory)
    root.putChild(helper.str_to_utf8("ws"), ws_resource)

    # start listining
    print("web server starting on port:", port)
    reactor.listenTCP(8000, site)
    reactor.run()
