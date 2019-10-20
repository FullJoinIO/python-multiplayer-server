import threading, time, json, queue, sys
 
from server.game_entities.player import Player
from server.utils.loop_factory import LoopFactory
from server.game_core import GameCore
 
class GameServer:
 
    def __init__(self, webserver):
        self.webserver = webserver
        self.player_count = 0
        self.rooms = []

        # TODO calcualte the amount of expected messages based on player count
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

        if self.player_count > 0:

            # Send update to each connected client
            for room in self.rooms:
    
                if room.player_count > 0:

                    payload = {
                        'server_stats': None,
                        'onp': None, # on new players
                        'opd': None, # on player diconnected
                        'opu': [], # on player update
                    }

                    # Sever stats
                    # TODO to be sent every few seconds instead on every tick                
                    payload['server_stats'] = {
                        'client_count_server': self.webserver.client_count,
                        'player_count_server': self.player_count,
                        'player_count_room': room.player_count
                    }

                    if len(room.new_players) > 0:
                        payload['onp'] = room.new_players.copy()
                        room.new_players.clear()

                    if len(room.disconnected_players) > 0:
                        payload['opd'] = room.disconnected_players.copy()
                        room.disconnected_players.clear()

                    # Take a snapshot each player state
                    for player in room.players.values():
                        payload['opu'].append({
                            player.id : {
                                'x': player.body.position.x,
                                'y': player.body.position.y
                            }
                        }
                    )
                    
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

        self.new_players = []
        self.disconnected_players = []
 
    def join(self, client):
        client.room = self
         
        player = Player(client.id)
        
        self.game_core.space.add(player.body, player.shape)
        self.players[player.id] = player

        self.new_players.append({
            'id': player.id, 
            'name': player.name
        })
         
        self.updatePlayerCount(client.id, 1)
 
    def leave(self, client):
        client.room = None

        player = self.players[client.id]
        self.game_core.space.remove(player.shape, player.body)
        self.disconnected_players.append(player.id)

        del self.players[player.id]
 
        self.updatePlayerCount(client.id, -1)
 
    def updatePlayerCount(self, client_id, value):
        self.player_count += value
        self.game_server.player_count += value
 
        # print(f"Player {client.id} has joined. Player count: {self.player_count}")
 
    def isFull(self):
        return True if self.player_count == self.capacity else False
        