import pygame as pg
from pygame.math import Vector2
from ..helpers.geometery import *

## TODO: Refactor collision sensing to use pos and angle, not 2 positions
## TODO: Reduce redundant intersection calculations for sensors in opposite
# TODO: Sensors need to be numbered and constantly reported
# directions
class Car(pg.sprite.Sprite):
    DODGER_BLUE = pg.Color('dodgerblue1')
    RED = (220, 0, 0)
    GREEN = (60, 220, 20)
    WHITE = (255, 255, 255)
    def __init__(self, pos, track_walls):
        ## Initialize
        super().__init__()

        # Two members required for a Sprite to draw itself- image, rect
        # Image defines the look
        # Rect defines the boundaries
        self.dimensions = (40,22)
        self.image = pg.Surface(self.dimensions, pg.SRCALPHA)
        self.image.fill(self.WHITE)
        self.rect = self.image.get_rect(center=pos)

        # Draw on our sprite surface to make it look like a triangle
        pg.draw.polygon(self.image, self.DODGER_BLUE, ((1, 1),
                        (self.dimensions[0] - 1, self.dimensions[1] / 2),
                        (1, self.dimensions[1] - 1)))

        # Store this so we know how to rotate relative to 0
        self.orig_img = self.image

        # Initialize
        self.pos = pg.math.Vector2(pos)
        self.vel = pg.math.Vector2(0, 0)
        self.track_walls = track_walls

        # Sensor variables
        self.vision_length = 250
        self.sensor_angles = [-160, -130, -90, -50, -20, 0, 20, 50, 90, 130,
                              160, 180]
        self.collisions = [self.vision_length for i in range(12)]
        self.dist_to_next_goal = 250

        # Car state variables
        # Having some speed ensures that vector angle is updated (try setting
        # it 0)
        self.speed = 0.0001
        self.sensors = []
        self.angle = self.vel.as_polar()[1]

    def update(self, next_goal):
        self.rotate()
        self.pos += self.vel
        self.rect.center = self.pos
        self.updateSensors()
        self.update_goal_dist(next_goal)
        self.senseCollisions()

    def rotate(self):
        # Keyboard example
        self.vel.from_polar((self.speed, self.angle))
        self.image = pg.transform.rotozoom(self.orig_img, -self.angle, 1)
        self.rect = self.image.get_rect(center=self.rect.center)

    def update_goal_dist(self, goal):
        self.dist_to_next_goal = distToPolygon(goal, self.pos)

    def updateSensors(self):
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

    def senseCollisions(self):
        collisions = []

        # Take each sensor line one at a time
        for sensor in self.sensors:
            sensor_detections = []
            # Detect the intersection of this sensor with each of the track
            # boundaries
            for fence in self.track_walls:
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