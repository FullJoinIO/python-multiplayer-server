import threading, time, json

from server.game_entities.player import Player
from server.utils.loop_factory import LoopFactory

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
            client.room.leave(client.id)

    def networkLoop(self):
        loop = LoopFactory(name = 'Network', tick_rate = 10)
        loop.simpleLoop(self.network_update)

    def network_update(self):
        # Send update to each connected client
        for room in self.rooms:

            # Sever stats payload
            # TODO to be sent every few seconds instead on every tick
            payload = {
                    "server_stats": {
                        "player_count_server": self.player_count,
                        "player_count_room": room.player_count 
                }
            }

            for player in room.players.values():
                player.client.sendMessage(str.encode(json.dumps(payload)), False)

class Room:
    def __init__(self, game_server, capacity):
        self.game_server = game_server
        self.players = {}
        self.capacity = capacity
        self.player_count = 0

    def join(self, client):
        client.room = self
        self.players[client.id] = Player(client)
        self.player_count += 1
        self.game_server.player_count += 1

        # print(f"Player {client.id} has joined. Player count: {self.player_count}")

    def leave(self, client_id):
        del self.players[client_id]
        self.player_count -= 1
        self.game_server.player_count -= 1

        # print(f"Player {client_id} has left. Player count: {self.player_count}")

    def isFull(self):
        return True if self.player_count == self.capacity else False
        




