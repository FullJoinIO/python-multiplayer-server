from server.game_entities.base_entity import BaseEntity
import pymunk

class Player (BaseEntity):

    def __init__(self, client_id):

        super().__init__()

        # Replace base auto generated id with client id
        self.id = client_id

        self.mass = 10
        self.radius = 25
        self.inertia = pymunk.moment_for_circle(self.mass, 0, self.radius, (0, 0))
        
        self.body = pymunk.Body(self.mass, self.inertia)
        self.body.position = 0, 0
        
        self.shape = pymunk.Circle(self.body, self.radius, (0, 0))
        self.shape.elasticity = 0.95
        self.shape.friction = 0.9
        
        