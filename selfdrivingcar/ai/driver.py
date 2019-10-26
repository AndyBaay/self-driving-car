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
    def __init__(self, vehicle, network, genome):
        ## Initialize
        super().__init__()
        self.vehicle = vehicle

        self.net = network
        self.genome = genome
        self.max_idle = 250

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

    def getMovement(self, score):
        self.fitness_current = score
        if self.fitness_current > self.current_max_fitness:
            self.current_max_fitness = self.fitness_current
            self.counter = 0
        else:
            self.counter += 1
        dead = self.counter > 250

        self.genome.fitness = score

        # Feed the sensor data in
        input_data = self.vehicle.collisions.copy()
        input_data.append(self.vehicle.dist_to_next_goal)
        #print("input is ", input_data )
        nnOutput = self.net.activate(input_data)
        #print(nnOutput)
        nn_key_press = self.updateKeys(nnOutput)
        #print(nn_key_press)

        # Turn off the feedback loop for now
        # ob, rew, done, info = env.step(nnOutput)
        #return our keystrokes and a boolean if we are stuck
        return nn_key_press
        #return pg.key.get_pressed()

    def updateKeys(self, choice_vector):
        key_strokes = {}
        for i in range(len(self.drive_options)):
            # Binarize the output of the nn
            key_strokes[self.drive_options[i]] = choice_vector[i] > 0.5
        return key_strokes

class HumanDriver:
    def __init__(self, vehicle):
        ## Initialize
        super().__init__()
        self.vehicle = vehicle

    def getMovement(self, ignore):
        return pg.key.get_pressed()