
class GameServer:

    def __init__(self, webserver):
        self.webserver = webserver
        self.rooms = []
        self.rooms.append(Room(5))

        self.commands = {
            "opj": self.onPlayerJoin,
            "opl": self.onPlayerLeave,
        }

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
        pass


class Room:
    def __init__(self, capacity):
        self.players = {}
        self.capacity = capacity
        self.player_count = 0

    def join(self, client):
        client.room = self
        self.players[client.id] = client
        self.player_count += 1

        print(f"Player {client.id} has joined. Player count: {self.player_count}")

    def leave(self, client_id):
        del self.players[client_id]
        self.player_count -= 1

        print(f"Player {client_id} has left. Player count: {self.player_count}")

    def isFull(self):
        return true if self.player_count == self.capacity else False
        




