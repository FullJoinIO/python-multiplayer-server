import threading, time
from datetime import datetime

from server.game_entities.player import Player

class GameServer:

    def __init__(self, webserver):
        self.webserver = webserver
        self.rooms = []
        self.rooms.append(Room(5))

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
        client.room.leave(client.id)

    def networkLoop(self):

        FPS = 10
        current_time = .0
        last_frame_time = .0

        print(f'Network Loop Thread started. FPS: {FPS}')

        while True:
            
            # d = datetime.now()
            # print(d)

            start_time = time.time()
            dt = start_time - last_frame_time
            last_frame_time = start_time

            self.network_update()

            sleep_time = 1./FPS - (time.time() - start_time)
            if sleep_time > 0:
                time.sleep(sleep_time)

    def network_update(self):
        for room in self.rooms:
            for player in room.players.values():
                player.client.sendMessage(str.encode(str(datetime.now())), False)

class Room:
    def __init__(self, capacity):
        self.players = {}
        self.capacity = capacity
        self.player_count = 0

    def join(self, client):
        client.room = self
        self.players[client.id] = Player(client)
        self.player_count += 1

        print(f"Player {client.id} has joined. Player count: {self.player_count}")

    def leave(self, client_id):
        del self.players[client_id]
        self.player_count -= 1

        print(f"Player {client_id} has left. Player count: {self.player_count}")

    def isFull(self):
        return True if self.player_count == self.capacity else False
        




