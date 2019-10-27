import pygame as pg
from random import randint
import neat
from abc import ABC, abstractmethod

class Driver(ABC):
    """
    Abstract class to define the interface for all drivers.
    """
    def __init__(self, vehicle):
        super().__init__()
        self.vehicle = vehicle

    @abstractmethod
    def get_movement(self):
        """ Given the car passed in, determine the movement to make """

    def set_vehicle(self, vehicle):
        self.vehicle = vehicle

    def remove_vehicle(self):
        self.vehicle = None


class RandomDriver(Driver):
    """
    Random driver that will select keys to press based on a random number
    generator
    """
    def __init__(self, vehicle):
        ## Initialize
        super().__init__(vehicle)

        ## Options ##
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


class NeatDriver(Driver):
    def __init__(self, vehicle, network, genome):
        ## Initialize
        super().__init__(vehicle)
        self.net = network
        self.genome = genome

        self.current_max_fitness = 0
        self.fitness_current = 0

        ## Options ##
        self.drive_options = [ pg.K_UP, pg.K_DOWN, pg.K_RIGHT, pg.K_LEFT ]

    def get_movement(self):
        """
        Feed our sensor data in the neural network and return the output
        :return: Dictionary of keys -> Boolean
        """
        self.fitness_current = self.vehicle.score
        if self.fitness_current > self.current_max_fitness:
            self.current_max_fitness = self.fitness_current

        self.genome.fitness = self.current_max_fitness

        input_data = self.vehicle.collisions + [self.vehicle.dist_to_next_goal]
        nn_output = self.net.activate(input_data)
        nn_key_press = self.map_output(nn_output)

        return nn_key_press

    def map_output(self, choice_vector):
        """
        Map numeric values in the choice vector to the driving option
        booleans needed to drive the car
        :param choice_vector: The numeric output corresponding to the
        activation of each driving input
        :return: Dictionary of keys -> Boolean
        """
        key_strokes = {}
        for i in range(len(self.drive_options)):
            # Binarize the output of the nn
            key_strokes[self.drive_options[i]] = choice_vector[i] > 0.5
        return key_strokes


class HumanDriver(Driver):
    def __init__(self, vehicle):
        ## Initialize
        super().__init__(vehicle)

    def get_movement(self):
        return pg.key.get_pressed()