import threading, time, json, queue, sys
 
from server.game_entities.player import Player
from server.utils.loop_factory import LoopFactory
from server.game_core import GameCore
 
class GameServer:
 
    def __init__(self, webserver):
        self.webserver = webserver
        self.player_count = 0
        self.rooms = []

        self.queue_batch_size = 10
        self.queue = queue.Queue()
 
        # Create rooms
        self.rooms.append(Room(self, 5))
        self.rooms.append(Room(self, 7))
 
        self.commands = {
            "opj": self.onPlayerJoin,
            "opl": self.onPlayerLeave,
        }
 
        # Spwan network loop thread
        thread = threading.Thread(target=self.networkLoop, args=())
        thread.start()
 
    def messageHandler(self, client, payload):        
        cmd = payload[0:3]
        data = payload[3:]

        # add message to a queue to be processed later
        self.queue.put({
            'cmd': cmd,
            'data': data,
            'client': client
        })
         
    def processQueue(self):

        # only process a fixed amount of events per tick
        for _ in range(self.queue_batch_size):
            try:
                obj = self.queue.get_nowait()
            except queue.Empty:
                break
            else:
                self.commands[obj['cmd']](obj['client'])

    def onPlayerJoin(self, client):
        # TODO add is server full
        for room in self.rooms:
            if not room.isFull():
                room.join(client)
                break
 
    def onPlayerLeave(self, client):
        if client.room:
            client.room.leave(client)
 
    def networkLoop(self):
        loop = LoopFactory(name = 'Network', tick_rate = 10)
        loop.simpleLoop(self.processQueue,
            self.sendNetworkUpdates
        )
 
    def sendNetworkUpdates(self):
        # Send update to each connected client
        for room in self.rooms:
 
            # Sever stats payload
            # TODO to be sent every few seconds instead on every tick
            payload = {
                    "server_stats": {
                        "client_count_server": self.webserver.client_count,
                        "player_count_server": self.player_count,
                        "player_count_room": room.player_count 
                }
            }
 
            payload = str.encode(json.dumps(payload))
            for player in room.players.values():
                self.webserver.sendMessage(player.id, payload)

 
class Room:
    def __init__(self, game_server, capacity):
        self.game_server = game_server
        self.game_core = GameCore(self)
         
        self.players = {}
        self.player_count = 0
        self.capacity = capacity
 
    def join(self, client):
        client.room = self
         
        player = Player(client.id)
        
        self.game_core.space.add(player.body, player.shape)
        self.players[player.id] = player
         
        self.updatePlayerCount(client.id, 1)
 
    def leave(self, client):
        client.room = None

        player = self.players[client.id]
        self.game_core.space.remove(player.shape, player.body)

        del self.players[player.id]
 
        self.updatePlayerCount(client.id, -1)
 
    def updatePlayerCount(self, client_id, value):
        self.player_count += value
        self.game_server.player_count += value
 
        # print(f"Player {client.id} has joined. Player count: {self.player_count}")
 
    def isFull(self):
        return True if self.player_count == self.capacity else False
        