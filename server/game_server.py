import threading, time, json
 
from server.game_entities.player import Player
from server.utils.loop_factory import LoopFactory
from server.game_core import GameCore
 
class GameServer:
 
    def __init__(self, webserver):
        self.webserver = webserver
        self.player_count = 0
        self.rooms = []
 
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
        self.commands[cmd](client)
         
    def onPlayerJoin(self, client):
        for room in self.rooms:
            if not room.isFull():
                room.join(client)
                break
 
    def onPlayerLeave(self, client):
        if client.room:
            client.room.leave(client)
 
    def networkLoop(self):
        loop = LoopFactory(name = 'Network', tick_rate = 10)
        loop.simpleLoop(self.processPlayerQueues, self.sendNetworkUpdates)
 
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
     
    def processPlayerQueues(self):
 
        for room in self.rooms:
 
            join_queue_removed_keys = []
            leave_queue_removed_keys = []
 
            # Add player to the world
            for key in room.player_joining_queue.keys():
                player = room.player_joining_queue[key]
                room.game_core.space.add(player.body, player.shape)
                 
                room.players[player.id] = player
                join_queue_removed_keys.append(player.id)
 
            # Remove player from the world
            for key in room.player_leaving_queue.keys():
                player = room.players[key]
                room.game_core.space.remove(player.shape, player.body)
 
                del room.players[player.id]
                leave_queue_removed_keys.append(player.id)
 
            # Remove keys from dicts after they've been iterated
            for key in join_queue_removed_keys:
                del room.player_joining_queue[key]
 
            for key in leave_queue_removed_keys:
                del room.player_leaving_queue[key]
 
class Room:
    def __init__(self, game_server, capacity):
        self.game_server = game_server
        self.game_core = GameCore(self)
         
        self.players = {}
        self.player_count = 0
        self.capacity = capacity
         
        self.player_joining_queue = {}
        self.player_leaving_queue = {}
 
    def join(self, client):
        client.room = self
         
        self.player_joining_queue[client.id] = Player(client.id)
         
        self.updatePlayerCount(client.id, 1)
 
    def leave(self, client):
        self.player_leaving_queue[client.id] = client
 
        self.updatePlayerCount(client.id, -1)
 
    def updatePlayerCount(self, client_id, value):
        self.player_count += value
        self.game_server.player_count += value
 
        # print(f"Player {client.id} has joined. Player count: {self.player_count}")
 
    def isFull(self):
        return True if self.player_count == self.capacity else False
        