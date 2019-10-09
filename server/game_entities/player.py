class Player:

    def __init__(self, client):
        self.id = client.id
        self.client = client
        self.pos = {'x': 0, 'y': 0}