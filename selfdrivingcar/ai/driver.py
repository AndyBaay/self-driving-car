import pygame as pg
from random import randint
import neat

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

class NeatDriver():
    def __init__(self, vehicle, genome, config):
        ## Initialize
        super().__init__()
        self.vehicle = vehicle

        self.net = neat.nn.recurrent.RecurrentNetwork.create(genome, config)

        self.current_max_fitness = 0
        self.fitness_current = 0
        self.frame = 0

        done = False

        ## Options ##
        ## Can press forward || backward || right || left
        self.drive_options = [ pg.K_UP, pg.K_DOWN, pg.K_RIGHT, pg.K_LEFT ]

        ## Frames delay for sticking to a decision
        self.counter = 0
        self.output = {pg.K_UP: False, pg.K_DOWN: False, pg.K_RIGHT: False, pg.K_LEFT: False }

    def getMovement(self):
        self.counter += 1

        # Feed the sensor data in
        nnOutput = self.net.activate(self.vehicle.collisions)

        # Turn off the feedback loop for now
        # ob, rew, done, info = env.step(nnOutput)
        #return ob
        return pg.key.get_pressed()

class HumanDriver:
    def __init__(self, vehicle):
        ## Initialize
        super().__init__()
        self.vehicle = vehicle

    def getMovement(self):
        return pg.key.get_pressed()