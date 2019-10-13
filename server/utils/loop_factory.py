import time
from datetime import datetime

class LoopFactory:

    def __init__(self, **kwargs):

        self.tick_rate = kwargs['tick_rate']
        self.name = kwargs['name']
        self.current_time = .0
        self.start_time = .0
        self.last_frame_time = .0
        self.dt =.0

        print(f'{self.name} Loop Thread started at {self.tick_rate} Hz.')
    
    def simpleLoop(self, *args):
        
        sleep_time = .0
        while True:
            
            #d = datetime.now()
            #print(d)

            self.current_time = time.time()
            self.start_time = self.current_time
            self.dt = self.start_time - self.last_frame_time
            self.last_frame_time = self.start_time

            for function in args:
                function()

            sleep_time = 1./self.tick_rate - (time.time() - self.start_time)
            if sleep_time > 0:
                time.sleep(sleep_time)