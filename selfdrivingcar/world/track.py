import pygame as pg
import os
from ..helpers.geometery import find_overlap

class MonzoTrack(pg.sprite.Sprite):
    TRACK_BOUNDRY_COLOR = (220, 0, 0)
    TRACK_BOUNDRY_COLOR = (255, 255, 255)
    TRACK_ASPHALT_COLOR = (60, 60, 60)
    TRACK_OB_COLOR = (107, 188, 255)
    GREEN = (60, 220, 20)
    TRACK_INNER = [(385, 256), (369, 295), (224, 308), (178, 502), (372, 637),
              (751, 616), (1005, 594), (1169, 569), (1186, 521), (1130, 456),
              (1029, 412), (990, 364), (1005, 309), (1102, 252), (1282, 144),
              (1306, 99), (1271, 72), (468, 134), (414, 173), (385, 256)]
    TRACK_OUTER = [(334, 215), (323, 237), (293, 248), (222, 255), (172, 270),
              (120, 403), (81, 506), (321, 730), (1248, 640), (1286, 588),
              (1274, 509), (1228, 459), (1179, 419), (1091, 377), (1063, 357),
              (1063, 341), (1100, 311), (1195, 273), (1307, 206), (1376, 140),
              (1379, 69), (1336, 23), (431, 79), (370, 114), (334, 215)]
    BOUNDARIES=[
            [ (81, 506), (321, 730), (1248, 640), (1286, 588),
                (1274, 509), (1228, 459), (1179, 419), (1091, 377), (1063, 357),
                (1437, 328), (1436, 797), (0, 796), (0, 264), (172, 270) ],
            [ (79, 505), (1, 505), (1, 1),(1438, 1),(1438, 505),
                (1179, 419), (1091, 377), (1063, 357),
                (1063, 341), (1100, 311), (1195, 273), (1307, 206), (1376, 140),
                (1379, 69), (1336, 23), (431, 79), (370, 114), (334, 215),
                (334, 215), (323, 237), (293, 248), (222, 255), (172, 270)
            ]
        ]
    # Out of bounds
    ob_bottom = [(81, 506), (321, 730), (1248, 640), (1286, 588),
                 (1274, 509), (1228, 459), (1179, 419), (1091, 377), (1063, 357),
                 (1437, 328), (1436, 797), (0, 796), (0, 264), (172, 270)]
    ob_top = [(79, 505), (0, 505), (0, 0), (1438, 0), (1438, 505),
              (1179, 419), (1091, 377), (1063, 357),
              (1063, 341), (1100, 311), (1195, 273), (1307, 206), (1380, 140),
              (1380, 69), (1336, 23), (431, 79), (370, 114), (334, 215),
              (334, 215), (323, 237), (293, 248), (222, 255), (172, 270)]
    # Top is less than 390, bottom is greater than 390
    cutoff_point = 390
    detection_zone = [ob_top, ob_bottom, TRACK_INNER]


    BOUNDARIES.append(TRACK_INNER)
    TRACK_GATES=[[(470, 146), (460, 75)],[(540, 141), (526, 64)],
                 [(603, 134), (595, 58)],[(663, 128), (654, 53)],
                 [(731, 123), (720, 54)],[(804, 117), (796, 42)],
                 [(873, 113), (863, 37)],[(945, 113), (926, 28)],
                 [(992, 94), (992, 41)],[(1064, 97),(1064, 28)],
                 [(1135, 122), (1141, 21)],[(1210, 87), (1214, 15)],
                 [(1264, 88), (1291, 13)],[(1288, 111), (1364, 62)],
                 [(1269, 133), (1367, 186)],[(1220, 165), (1286, 253)],
                 [(1171, 199), (1228, 297)],[(1110, 237), (1157, 317)],
                 [(1049, 276), (1106, 350)],[(975, 361), (1107, 370)],
                 [(1019, 416), (1111, 374)],[(1104, 450), (1136, 400)],
                 [(1122,480), (1200, 437)],[(1156, 514), (1280, 528)],
                 [(1148, 552), (1274, 655)],[(1104, 569), (1110, 649)],
                 [(987, 571), (1013, 676)],[(897, 590), (896, 691)],
                 [(779,606), (773, 697)],[(704, 607), (691, 692)],
                 [(612, 613), (611, 715)],[(525, 619), (523, 718)],
                 [(444, 624), (446, 724)],[(382, 623), (332, 738)],
                 [(338, 589), (276, 708)],[(276, 542), (210, 628)],
                 [(235, 485), (134, 580)],[(182, 496), (75, 495)],
                 [(193, 460), (101, 425)],[(214, 414), (128, 354)],
                 [(221, 360), (136, 300)],[(238, 318), (192, 250)],
                 [(299, 313), (284, 230)],[(369, 311), (293, 226)],
                 [(396, 255), (297, 209)],[(407, 206), (303, 148)],
                 [(432, 165), (368, 92)]
                 ]
    OTHER_GATES=[]
    TRACK = [TRACK_INNER, TRACK_OUTER]
    TEST_TRACK = [[(100,500), (100,100), (500,100)],
                  [(200, 500), (200, 200), (500, 200)]]
    def __init__(self, width, height):
        ## Initialize
        super().__init__()

        # Two members required for a Sprite to draw itself- image, rect
        # Image defines the look
        # Rect defines the boundaries
        self.dimensions = (width, height)
        self.image = pg.Surface(self.dimensions, pg.SRCALPHA)
        self.image.fill(self.TRACK_ASPHALT_COLOR)
        self.rect = self.image.get_rect()
        self.track_squares = self.create_incentive_squares(self.TRACK_GATES)
        self.squares_in_use = set()


    def update(self):
        self.image.fill(self.TRACK_ASPHALT_COLOR)
        for gate in self.TRACK_GATES:
            pg.draw.line(self.image, self.GREEN, gate[0], gate[1], 3)
        for sq in self.squares_in_use:
            pg.draw.polygon(self.image, self.GREEN,
                        self.track_squares[sq])
        pg.draw.line(self.image, (255,255,255), (1064, 97),(1064, 28), 7)
        for ob in self.detection_zone:
            pg.draw.polygon(self.image, self.TRACK_OB_COLOR, ob)
        for side in self.TRACK:
            pg.draw.lines(self.image, self.TRACK_BOUNDRY_COLOR, False, side, 3)

        self.squares_in_use = set()

    def check_out_of_bounds(self, rect):
        rect_coords = [rect.topleft,
            rect.topright,
            rect.bottomright,
            rect.bottomleft]
        polys = []
        area = 0
        for ob in self.detection_zone:
            p, a = find_overlap(ob, rect_coords)
            polys.append(p)
            area += a
        return area


    ## Used to make squares from the track boundaries ##
    def create_incentive_squares(self, lines):
        squares=[]
        for i in range(len(lines)):
            reverse_list = lines[ (i + 1) % len(lines)]
            if (i % 2 == 0):
                reverse_list.reverse()
            squares += [lines[i] + reverse_list]
        return squares
