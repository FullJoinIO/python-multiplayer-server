import pymunk, threading

from server.utils.loop_factory import LoopFactory
from server.game_entities.base_entity import BaseEntity

collision_types = {
    "player": 1,
    "floor": 2,
}


class GameCore:
    
    def __init__(self, room):
        self.room = room
        self.space = pymunk.Space()      # Create a Space which contain the simulation
        self.space.gravity = 0,-1000     # Set its gravity

        self.createWorld()
        
        thread = threading.Thread(target=self.gameLoop, args=())
        thread.start()

    def createWorld(self):
        # floor
        floor = BaseEntity() 
        floor.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        floor.body.position = 0,-200
        
        floor.shape = pymunk.Segment(floor.body, (-150,0), (150,0), 20)
        #floor.shape.color = THECOLORS["red"]
        floor.shape.elasticity = 1.0
        #floor.shape.collision_type = collision_types["floor"]
        self.space.add(floor.body, floor.shape)


    def gameLoop(self):
        loop = LoopFactory(name = "Game", tick_rate = 30)
        loop.simpleLoop(self.simulation)

    def simulation(self):
        self.space.step(0.02)        # Step the simulation one step forward
