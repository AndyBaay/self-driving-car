import pygame as pg
from pygame.math import Vector2
from ..helpers.geometery import *
import os


## TODO: Refactor collision sensing to use pos and angle, not 2 positions
## TODO: Reduce redundant intersection calculations for sensors in opposite
# TODO: Sensors need to be numbered and constantly reported
# directions
class Car(pg.sprite.Sprite):
    RED = (220, 0, 0)
    GREEN = (60, 220, 20)
    STEERING_SENSITIVITY = 5
    def __init__(self, name, pos, race_track):
        ## Initialize
        super().__init__()

        # Two members required for a Sprite to draw itself- image, rect
        # Image defines the look
        # Rect defines the boundaries
        self.dimensions = (40,22)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "../../assets/Renault_clear.png")

        self.image = pg.image.load(image_path)
        self.rect = self.image.get_rect(center=pos)
        self.name = name

        # Store this so we know how to rotate relative to 0
        self.orig_img = self.image

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

        # Track variables
        self.race_track = race_track
        self.track_zones = self.race_track.track_squares
        self.current_zone, self.next_zone = find_square_conatining(
            self.track_zones, self.pos, 0)
        self.dist_to_next_goal = self.vision_length

        # Game variables
        self.score = 0
        self.alive = True

    def update(self, keys_pressed):
        self.move_car(keys_pressed)
        self.rotate()
        self.pos += self.vel
        self.rect.center = self.pos
        self.update_sensors()
        self.update_goal_dist()
        self.sense_collisions()

    def rotate(self):
        # Keyboard example
        self.vel.from_polar((self.speed, self.angle))
        self.image = pg.transform.rotozoom(self.orig_img, -self.angle, 1)
        self.rect = self.image.get_rect(center=self.rect.center)

    def update_goal_dist(self):
        c, n = find_square_conatining(
            self.track_zones, self.pos, self.current_zone, 3)
        if c is not None: self.current_zone = c
        if n is not None:
            # We have moved forward on the track, +1 points
            if n != self.next_zone:
                self.score += 1
                self.next_zone = n
                print(self.name, " scores +1, current total: ", self.score)

        self.dist_to_next_goal = distToPolygon(self.track_zones[self.next_zone],
                          self.pos)
        self.race_track.squares_in_use.add(self.next_zone)

    def move_car(self, inputs):
        keys = inputs
        if keys[pg.K_UP]:
            self.speed += .2
        elif keys[pg.K_DOWN]:
            self.speed -= .2

        if keys[pg.K_RIGHT]:
            self.angle += self.STEERING_SENSITIVITY
        elif keys[pg.K_LEFT]:
            self.angle -= self.STEERING_SENSITIVITY


    def update_sensors(self):
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
        collisions = []

        # Take each sensor line one at a time
        for sensor in self.sensors:
            sensor_detections = []
            # Detect the intersection of this sensor with each of the track
            # boundaries
            for fence in self.race_track.BOUNDARIES:
                for i in range(len(fence) - 1):
                    wall = (fence[i], fence[i + 1])
                    c_point = findIntersection(sensor, wall)
                    if c_point is not None: sensor_detections.append(c_point)

            # Now keep only the closest hit
            min_dist = self.vision_length
            closest_collision = None
            for col in sensor_detections:
                d = pointDistance(col, self.pos)
                if d < min_dist:
                    min_dist = d
                    closest_collision = col
            # Add closest hit to collisions to be drawn and reported back
            #if closest_collision is not None:
                #collisions.append((self.pos, closest_collision, min_dist))
            collisions.append(min_dist)

        self.collisions = collisions