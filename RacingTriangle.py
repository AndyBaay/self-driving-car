import sys
import pygame as pg
from pygame.math import Vector2
import math

### GLOBALS ###
DODGER_BLUE = pg.Color('dodgerblue1')
RED = (220, 0, 0)
TRACK_INNER = [(385, 256), (369, 295), (224, 308), (178, 502), (372, 637),
          (751, 616), (1005, 594), (1169, 569), (1186, 521), (1130, 456),
          (1029, 412), (990, 364), (1005, 309), (1102, 252), (1282, 144),
          (1306, 99), (1271, 72), (468, 134), (414, 173), (385, 256)]
TRACK_OUTER = [(334, 215), (323, 237), (293, 248), (222, 255), (172, 270),
          (120, 403), (81, 506), (321, 730), (1248, 640), (1286, 588),
          (1274, 509), (1228, 459), (1179, 419), (1091, 377), (1063, 357),
          (1063, 341), (1100, 311), (1195, 273), (1307, 206), (1376, 140),
          (1379, 69), (1336, 23), (431, 79), (370, 114), (334, 215)]
TRACK = [TRACK_INNER, TRACK_OUTER]
TEST_TRACK = [[(100,500), (100,100), (500,100)],
              [(200, 500), (200, 200), (500, 200)]]


## Helper functions for calculating collisions ##
def isBetween(a, b, c):
    dotproduct = (c[0] - a[0]) * (b[0] - a[0]) + (c[1] - a[1])*(b[1] - a[1])
    if dotproduct < 0:
        return False

    squaredlengthba = (b[0] - a[0])*(b[0] - a[0]) + (b[1] - a[1])*(b[1] - a[1])
    if dotproduct > squaredlengthba:
        return False

    return True

def det(a, b):
    return a[0] * b[1] - a[1] * b[0]

def findIntersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    div = det(xdiff, ydiff)
    if div == 0:
       return None

    d = (det(*line1), det(*line2))
    x_i = det(d, xdiff) / div
    y_i = det(d, ydiff) / div

    # Test to make sure that the line we are using is on the wall segment
    if isBetween(line2[0], line2[1], (x_i, y_i)) and \
            isBetween(line1[0], line1[1], (x_i, y_i)):
        return x_i, y_i
    else: return None

def pointDistance(p1, p2):
    return math.sqrt(((p1[0] - p2[0]) ** 2) + ((p1[1] - p2[1]) ** 2))


## TODO: Refactor collision sensing to use pos and angle, not 2 positions
## TODO: Reduce redundant intersection calculations for sensors in opposite
# directions
class Car(pg.sprite.Sprite):
    def __init__(self, pos, track_walls):
        ## Initialize
        super().__init__()

        # Two members required for a Sprite to draw itself- image, rect
        # Image defines the look
        # Rect defines the boundaries
        self.dimensions = (40,22)
        self.image = pg.Surface(self.dimensions, pg.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)

        # Draw on our sprite surface to make it look like a triangle
        pg.draw.polygon(self.image, DODGER_BLUE, ((1, 1),
                        (self.dimensions[0] - 1, self.dimensions[1] / 2),
                        (1, self.dimensions[1] - 1)))

        # Store this so we know how to rotate relative to 0
        self.orig_img = self.image

        # Initialize
        self.pos = pg.math.Vector2(pos)
        self.vel = pg.math.Vector2(0, 0)
        self.track_walls = track_walls

        # Sensor variables
        self.vision_length = 200
        self.sensor_angles = [-160, -130, -90, -50, -20, 0, 20, 50, 90, 130,
                              160, 180]
        self.collisions = []

        # Car state variables
        # Having some speed ensures that vector angle is updated (try setting
        # it 0)
        self.speed = 0.0001
        self.sensors = []
        self.angle = self.vel.as_polar()[1]

    def update(self):
        self.rotate()
        self.pos += self.vel
        self.rect.center = self.pos
        self.updateSensors()
        self.senseCollisions()


    def rotate(self):
        self.angle = (pg.mouse.get_pos()-self.pos).as_polar()[1]
        self.vel.from_polar((self.speed, self.angle))
        self.image = pg.transform.rotozoom(self.orig_img, -self.angle, 1)
        self.rect = self.image.get_rect(center=self.rect.center)

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
            min_dist = 100000
            closest_collision = None
            for col in sensor_detections:
                d = pointDistance(col, self.pos)
                if d < min_dist:
                    min_dist = d
                    closest_collision = col
            # Add closest hit to collisions to be drawn and reported back
            if closest_collision is not None:
                collisions.append((self.pos, closest_collision, min_dist))

        self.collisions = collisions

# TODO: Need to implement a Game class for a single track logic
# TODO: Need to add inputs as

def main():
    screen = pg.display.set_mode((1440, 800))
    clock = pg.time.Clock()
    car_sprites = pg.sprite.Group()
    boundary = TRACK
    #boundary = [[(100,100), (500,100)],
    #            [(100,100), (100,500)],
    #            [(200, 200), (500, 200)],
    #            [(200,200), (200,500)]]
    player = Car((300, 200), boundary)
    car_sprites.add(player)

    done = False
    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True

        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            player.speed += .2
        elif keys[pg.K_s]:
            player.speed -= .2

        car_sprites.update()
        screen.fill((30, 30, 30))
        for side in boundary:
            pg.draw.lines(screen, RED, False, side, 2)
        #for line in player.sensors:
        #    a, b = line
        #    pg.draw.line(screen, DODGER_BLUE, a, b, 2)
        for col in player.collisions:
            # Unpack position, collision, and distance
            p, c, d = col
            pg.draw.circle(screen, DODGER_BLUE, c, 5, 2)
            pg.draw.line(screen, DODGER_BLUE, p, c, 2)
        car_sprites.draw(screen)

        pg.display.flip()
        clock.tick(30)




if __name__ == '__main__':
    pg.init()
    main()
    pg.quit()
    sys.exit()