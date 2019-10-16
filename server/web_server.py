import sys, os, platform

sys.path.append("./")
# print('\n'.join(sys.path))

from pathlib import Path

from twisted.web import server, resource, static, http
from twisted.internet import reactor

from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol
from autobahn.twisted.resource import WebSocketResource

import server.utils.helper as helper
from server.game_server import GameServer

script_path = Path(os.path.dirname(__file__))
project_root_path = script_path.parent


class ServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        self.factory.register(self)

    def connectionLost(self, reason):
        self.factory.unregister(self)

    def onMessage(self, payload, isBinary):
        self.factory.onMessage(self, payload, isBinary) 


class ServerFactory(WebSocketServerFactory):

    def __init__(self, *args, **kwargs):

        super(ServerFactory, self).__init__(*args, **kwargs)
        self.clients = {}
        self.client_count = 0
        self.game_server = GameServer(self)

    def register(self, client):

        # Generate unique id and add client to list of managed connections.
        client.id = helper.get_uuid()
        
        client.room = None

        self.clients[client.id] = client
        self.client_count += 1
        
        #print(f"Client connecting: {client.peer} {client.id}")

    def unregister(self, client):

        #print(f"Client disconnected: {client.id}")

        # Remove client from list of managed connections.
        self.game_server.onPlayerLeave(client)

        del self.clients[client.id]
        self.client_count -= 1

    def onMessage(self, client, payload, isBinary):

        if isBinary:
            print(f"Binary message received: {len(payload)} bytes")
            print("Binary currently not support by message handler")
        else:
            self.game_server.messageHandler(client,payload.decode('utf8'))

    def sendMessage(self, cliend_id, payload):
        self.clients[cliend_id].sendMessage(payload, False)

class WebServer():

    def __init__(self, *args, **kwargs):
        
        port = 8000

        print(f"Python: {platform.python_version()}")
        print(f"Web server listening port: {port}")

        # Web server setup
        root = resource.Resource()

        rootPage = static.File(os.path.join(project_root_path,"client/index.html"))
        root.putChild(helper.str_to_utf8(''), rootPage)

        client_path = os.path.join(project_root_path, "client/")
        for file in os.listdir(client_path):
                root.putChild(helper.str_to_utf8(file), static.File(client_path + file))

        # Websocket over tcp setup
        factory = ServerFactory()
        factory.protocol = ServerProtocol
        factory.noisy = False
        ws_resource = WebSocketResource(factory)
        root.putChild(helper.str_to_utf8("ws"), ws_resource)

        # Server listining
        site = server.Site(root)
        reactor.listenTCP(port, site)
        reactor.run()



if __name__ == "__main__":
    web_server = WebServer()