import server.utils.helper as helper

class BaseEntity:

    def __init__(self):

        self.id = helper.get_uuid()
        self.pos = {'x': None, 'y': None}

        self.body = None
        self.shape = None