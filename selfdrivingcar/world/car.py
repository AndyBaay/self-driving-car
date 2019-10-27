import os
import pygame as pg
from pygame.math import Vector2
from ..helpers.geometery import *
from ..ai.driver import *


class Car(pg.sprite.Sprite):
    """
    A Car object for driving around the track
    """

    # Appearances
    RED = (220, 0, 0)
    GREEN = (60, 220, 20)

    # Driving Parameters
    STEERING_SENSITIVITY = 5
    MAX_DIST_TO_GOAL = 200
    MAX_IDLE = 200
    MAX_OB_AREA=1600

    def __init__(self, name, pos, race_track):
        """
        Initialize the object
        :param name: The name of this car, as there can be many on the track
        :param pos: starting (x, y) position of the car
        :param race_track: Track object so our car can understand the world
        :return: None
        """
        super().__init__()
        self.name = name

        # Initialize the two members required for a Sprite to work- image & rect
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "../../assets/Renault_Racer.png")
        self.image = pg.image.load(image_path)
        self.rect = self.image.get_rect(center=pos)
        self.dimensions = self.image.get_rect().size

        # Store this for future reference because transformations in update()
        # are destructive so the image will degrade over time
        self.orig_img = self.image.copy()

        # Initialize location/velocity
        self.pos = pg.math.Vector2(pos)
        self.vel = pg.math.Vector2(0, 0)
        # Having some speed ensures that vector angle is updated (try setting
        # it 0)
        self.speed = 0.0001
        self.angle = self.vel.as_polar()[1]

        # Sensor variables
        self.sensors = []
        self.vision_length = 250
        self.sensor_angles = [-160, -130, -90, -50, -20, 0, 20, 50, 90, 130,
                              160, 180]
        self.collisions = [self.vision_length for i in range(12)]
        self.area_ob = 0

        # Track variables
        self.race_track = race_track
        self.track_zones = self.race_track.track_squares
        self.current_zone, self.next_zone = find_square_conatining(
            self.track_zones, self.pos, 0)
        self.dist_to_next_goal = self.vision_length

        # Game variables
        self.score = 0
        self.last_scored_timer = 0
        self.alive = True

        # Driver
        self.driver = HumanDriver(self)


    def add_driver(self, new_driver):
        """
        Add or replace the driver of the car
        """
        self.driver = new_driver

    def update(self):
        """
        Update the car's position, sensors, and score for 1 frame iteration
        """
        self.move_car()
        self.rotate()
        self.update_sensors()
        self.update_goal_dist()
        self.sense_collisions()
        self.detect_out_of_bounds()


    def rotate(self):
        """
        Make sure the car image corresponds to its velocity and orientation
        """
        self.vel.from_polar((self.speed, self.angle))
        self.image = pg.transform.rotozoom(self.orig_img, -self.angle, 1)
        self.rect = self.image.get_rect(center=self.rect.center)


    def update_goal_dist(self):
        """
        The track is split into zones, determine which zone we are in
        currently, the next one we need to get to, and the distance to it.
        """
        current_square, next_square = find_square_conatining(
            self.track_zones, self.pos, self.current_zone, 3)
        if current_square is not None: self.current_zone = current_square
        if next_square is not None:
            # We have moved forward on the track, +1 points
            if next_square != self.next_zone:
                self.score += 1
                self.next_zone = next_square
                self.last_scored_timer = 0
            else:
                self.last_scored_timer += 1

        self.dist_to_next_goal = distToPolygon(self.track_zones[self.next_zone],
                                               self.pos)
        self.race_track.squares_in_use.add(self.next_zone)
        if (self.dist_to_next_goal > self.MAX_DIST_TO_GOAL or
                self.last_scored_timer > self.MAX_IDLE):
            self.alive = False

    def move_car(self):
        """
        Update the velocity angle based on inputs from the driver
        """
        keys = self.driver.get_movement()
        if keys[pg.K_UP]:
            self.speed += .2
        elif keys[pg.K_DOWN]:
            self.speed -= .2
        if keys[pg.K_RIGHT]:
            self.angle += self.STEERING_SENSITIVITY
        elif keys[pg.K_LEFT]:
            self.angle -= self.STEERING_SENSITIVITY
        self.pos += self.vel
        self.rect.center = self.pos


    def update_sensors(self):
        """
        Update the sensor vectors now that the position of the car has changed
        """
        sens = [] # reset sensor array
        # For each angle offset, create a vector and store it
        for a in self.sensor_angles:
            # A zero vector
            vector = Vector2()
            # Update vector using magnitude and angle
            vector.from_polar((self.vision_length, self.angle + a))
            # Add the vector to current position to get the end point.
            sens.append((self.pos, self.pos + vector))
        self.sensors = sens


    def sense_collisions(self):
        """
        Detect the nearest collision for each sensor in the array
        """
        collisions =[]

        # Take each sensor line one at a time
        for sensor in self.sensors:
            sensor_detections = []
            # Detect the intersection of this sensor with each of the track
            # boundaries
            for fence in self.race_track.TRACK_LIMITS:
                for i in range(len(fence) - 1):
                    wall = (fence[i], fence[i + 1])
                    c_point = find_intersection(sensor, wall)
                    if c_point is not None: sensor_detections.append(c_point)

            # Now keep only the closest hit
            min_dist = self.vision_length
            for col in sensor_detections:
                d = point_distance(col, self.pos)
                if d < min_dist:
                    min_dist = d
            collisions.append(min_dist)

        self.collisions = collisions


    def detect_out_of_bounds(self):
        """
        Determine if the car is completely off-track
        """
        self.area_ob = self.race_track.check_out_of_bounds(self.rect)
        if self.area_ob > self.MAX_OB_AREA:
            self.alive = False