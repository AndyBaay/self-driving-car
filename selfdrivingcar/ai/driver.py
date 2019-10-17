import pygame as pg
from random import randint

class RandomDriver():
    def __init__(self, vehicle):
        ## Initialize
        super().__init__()
        self.vehicle = vehicle

        ## Options ##
        ## Can press forward || backward &&
        ## right || left
        self.drive_options = [pg.K_UP, pg.K_DOWN, None]
        self.steer_options = [pg.K_RIGHT, pg.K_LEFT, None]

        ## Frames delay for sticking to a decision
        self.counter = 0
        self.output = {pg.K_UP: False, pg.K_DOWN: False, pg.K_RIGHT: False, pg.K_LEFT: False }

    def getMovement(self):
        self.counter += 1

        if self.counter % 10 == 0:
            drive = self.drive_options[randint(0,2)]
            steer = self.steer_options[randint(0,2)]
            keys = {pg.K_UP: False, pg.K_DOWN: False, pg.K_RIGHT: False, pg.K_LEFT: False }
            if drive is not None:
                keys[drive]=True
            if steer is not None:
                keys[steer]=True
            self.output = keys
        return self.output
