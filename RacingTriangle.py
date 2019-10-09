import sys
import pygame as pg
from pygame.math import Vector2
import math
import matplotlib.path as mpltPath
from shapely.geometry import Polygon, Point, LinearRing

### GLOBALS ###
DODGER_BLUE = pg.Color('dodgerblue1')
RED = (220, 0, 0)
GREEN = (60, 220, 20)
WHITE = (255, 255, 255)

TRACK_INNER = [(385, 256), (369, 295), (224, 308), (178, 502), (372, 637),
          (751, 616), (1005, 594), (1169, 569), (1186, 521), (1130, 456),
          (1029, 412), (990, 364), (1005, 309), (1102, 252), (1282, 144),
          (1306, 99), (1271, 72), (468, 134), (414, 173), (385, 256)]
TRACK_OUTER = [(334, 215), (323, 237), (293, 248), (222, 255), (172, 270),
          (120, 403), (81, 506), (321, 730), (1248, 640), (1286, 588),
          (1274, 509), (1228, 459), (1179, 419), (1091, 377), (1063, 357),
          (1063, 341), (1100, 311), (1195, 273), (1307, 206), (1376, 140),
          (1379, 69), (1336, 23), (431, 79), (370, 114), (334, 215)]
TRACK_GATES=[[(470, 146), (460, 75)],
             [(540, 141), (526, 64)],
             [(603, 134), (595, 58)],
             [(663, 128), (654, 53)],
             [(731, 123), (720, 54)],
             [(804, 117), (796, 42)],
             [(873, 113), (863, 37)],
             [(945, 113), (926, 28)],
             [(992, 94), (992, 41)],
             [(1064, 97),(1064, 28)],
             [(1135, 122), (1141, 21)],
             [(1210, 87), (1214, 15)],
             [(1264, 88), (1291, 13)],
             [(1288, 111), (1364, 62)],
             [(1269, 133), (1367, 186)],
             [(1220, 165), (1286, 253)],
             [(1171, 199), (1228, 297)],
             [(1110, 237), (1157, 317)],
             [(1049, 276), (1106, 350)],
             [(975, 361), (1107, 370)],
             [(1019, 416), (1111, 374)],
             [(1104, 450), (1136, 400)],
             [(1122,480), (1200, 437)],
             [(1156, 514), (1280, 528)],
             [(1148, 552), (1274, 655)],
             [(1104, 569), (1110, 649)],
             [(987, 571), (1013, 676)],
             [(897, 590), (896, 691)],
             [(779,606), (773, 697)],
             [(704, 607), (691, 692)],
             [(612, 613), (611, 715)],
             [(525, 619), (523, 718)],
             [(444, 624), (446, 724)],
             [(382, 623), (332, 738)],
             [(338, 589), (276, 708)],
             [(276, 542), (210, 628)],
             [(235, 485), (134, 580)],
             [(182, 496), (75, 495)],
             [(193, 460), (101, 425)],
             [(214, 414), (128, 354)],
             [(221, 360), (136, 300)],
             [(238, 318), (192, 250)],
             [(299, 313), (284, 230)],
             [(369, 311), (293, 226)],
             [(396, 255), (297, 209)],
             [(407, 206), (303, 148)],
             [(432, 165), (368, 92)]
             ]
OTHER_GATES=[]
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

def distToPolygon(poly_points, start_point):
    poly = Polygon(poly_points)
    point = Point(start_point[0], start_point[1])

    pol_ext = LinearRing(poly.exterior.coords)
    d = pol_ext.project(point)
    p = pol_ext.interpolate(d)
    c = list(p.coords)[0]
    return pointDistance(start_point, c)

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
        # Mouse following example
        #self.angle = (pg.mouse.get_pos()-self.pos).as_polar()[1]

        # Keyboard example
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


class ScoreBoard(pg.sprite.Sprite):
    def __init__(self, pos):
        ## Initialize
        super().__init__()
        # Two members required for a Sprite to draw itself- image, rect
        # Image defines the look
        # Rect defines the boundaries
        self.dimensions = (105, 75)
        self.image = pg.Surface(self.dimensions)
        self.rect = self.image.get_rect(center=pos)
        self.image.fill(WHITE)
        self.font = pg.font.Font('freesansbold.ttf', 32)
        self.header = self.font.render(' Score ', True, GREEN,
                                       DODGER_BLUE)
        self.image.blit(self.header,(0,0))
        self.score = 0

    def update(self, *args):
        self.text = self.font.render("{0}".format(self.score),True,(0,0,0))

        self.image.fill(WHITE)
        self.image.blit(self.header,(0,0))
        self.image.blit(self.text,(0,40))

    def scoreInc(self, amount):
        self.score += amount




def create_incentive_squares(lines):
    squares=[]
    for i in range(len(lines)):
        reverse_list = lines[ (i + 1) % len(lines)]
        if (i % 2 == 0):
            reverse_list.reverse()
        squares += [lines[i] + reverse_list]
    return squares

def find_square_conatining (squares, pos, checking_square = 0,
                            squares_lookahead = None):
    if squares_lookahead is None: squares_lookahead = len(squares)
    found_square=None
    while found_square is None and squares_lookahead > 0:
        path = mpltPath.Path(squares[checking_square])
        inside2 = path.contains_point(pos)
        if inside2:
            found_square = checking_square
            return found_square, (found_square + 1) % len(squares)
        checking_square = (checking_square + 1) % len(squares)
        squares_lookahead -= 1
    return found_square, None

# TODO: Need to add inputs as arrow keys
class Game:
    def __init__(self):
        pg.init()
        pg.display.set_caption("Car AI")
        width = 1440
        height = 800
        self.screen = pg.display.set_mode((width, height))
        self.clock = pg.time.Clock()
        self.ticks = 60
        self.exit = False

        self.car_sprites = pg.sprite.Group()
        self.text_sprites = pg.sprite.Group()
        self.score_sprites = pg.sprite.Group()
        self.boundary = TRACK
        self.track_squares = create_incentive_squares(TRACK_GATES)
        self.STEERING_SENSITIVITY=5

        self.player = Car((946, 74), self.boundary)
        self.score = ScoreBoard((80,60))
        self.car_sprites.add(self.player)
        self.text_sprites.add(self.score)

        # Determine starting square:
        self.car_square, self.next_square= find_square_conatining(
            self.track_squares, self.player.pos)
        print(self.car_square)

    def run(self):
        while not self.exit:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.exit = True

            keys = pg.key.get_pressed()
            if keys[pg.K_UP]:
                self.player.speed += .2
            elif keys[pg.K_DOWN]:
                self.player.speed -= .2

            if keys[pg.K_RIGHT]:
                self.player.angle += self.STEERING_SENSITIVITY
            elif keys[pg.K_LEFT]:
                self.player.angle -= self.STEERING_SENSITIVITY

            # Check if we made it to the next square
            c, n = find_square_conatining(
                self.track_squares, self.player.pos, self.car_square, 3)
            if c is not None: self.car_square = c
            if n is not None:
                # We have moved forward on the track, +1 points
                if n != self.next_square: self.score.scoreInc(1)
                self.next_square = n
            d = distToPolygon(self.track_squares[self.next_square],
                              self.player.pos)

            # Sprites
            self.car_sprites.update()
            self.text_sprites.update()
            self.screen.fill((30, 30, 30))
            for side in self.boundary:
                pg.draw.lines(self.screen, RED, False, side, 2)
            pg.draw.polygon(self.screen, GREEN,
                            self.track_squares[self.car_square])
            pg.draw.polygon(self.screen, RED,
                            self.track_squares[self.next_square])
            for gate in TRACK_GATES:
                pg.draw.line(self.screen, GREEN, gate[0], gate[1], 3)
            for col in self.player.collisions:
                # Unpack position, collision, and distance
                p, c, d = col
                pg.draw.circle(self.screen, DODGER_BLUE, c, 5, 2)
                pg.draw.line(self.screen, DODGER_BLUE, p, c, 2)
            self.car_sprites.draw(self.screen)
            self.text_sprites.draw(self.screen)

            pg.display.flip()
            self.clock.tick(30)
        pg.quit()


def main():
    screen = pg.display.set_mode((1440, 800))
    clock = pg.time.Clock()
    car_sprites = pg.sprite.Group()
    boundary = TRACK
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
        for gate in TRACK_GATES:
            pg.draw.line(screen,GREEN, gate[0], gate[1], 3)
        for col in player.collisions:
            # Unpack position, collision, and distance
            p, c, d = col
            pg.draw.circle(screen, DODGER_BLUE, c, 5, 2)
            pg.draw.line(screen, DODGER_BLUE, p, c, 2)
        car_sprites.draw(screen)

        pg.display.flip()
        clock.tick(30)
    pg.quit()

if __name__ == '__main__':
    game = Game()
    game.run()
    sys.exit()