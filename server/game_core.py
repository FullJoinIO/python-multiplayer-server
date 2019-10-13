import pymunk, threading

from server.utils.loop_factory import LoopFactory

class GameCore:
    
    def __init__(self, room):
        self.room = room
        self.space = pymunk.Space()      # Create a Space which contain the simulation
        self.space.gravity = 0,-1000     # Set its gravity

        thread = threading.Thread(target=self.gameLoop, args=())
        thread.start()

    def gameLoop(self):
        loop = LoopFactory(name = "Game", tick_rate = 30)
        loop.simpleLoop(self.simulation)

    def simulation(self):
        self.space.step(0.02)        # Step the simulation one step forward
