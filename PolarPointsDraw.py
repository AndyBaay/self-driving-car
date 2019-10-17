import sys
import pygame as pg
from shapely.geometry import Polygon
from functools import reduce

class Player(pg.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pg.Surface((50, 30), pg.SRCALPHA)
        color = pg.Color('dodgerblue1')
        pg.draw.polygon(self.image, color, ((1, 1), (49, 15), (1, 29)))
        self.orig_img = self.image
        self.rect = self.image.get_rect(center=pos)
        self.pos = pg.math.Vector2(pos)
        self.vel = pg.math.Vector2(0, 0)
        self.speed = 0

    def update(self):
        self.rotate()
        self.pos += self.vel
        self.rect.center = self.pos

    def rotate(self):
        _, angle = (pg.mouse.get_pos()-self.pos).as_polar()
        self.vel.from_polar((self.speed, angle))
        self.image = pg.transform.rotozoom(self.orig_img, -angle, 1)
        self.rect = self.image.get_rect(center=self.rect.center)

def getCoords(polygon: Polygon):
    return list(polygon.exterior.coords)

def cliply(p1, p2):
    print(p1)
    print(p2)
    print("p1: ", p1, "p2: ", p2)
    a= Polygon(p1[0])
    b= Polygon(p2)
    intersection= a.intersection(b)
    print("intersection: ", intersection)
    if not intersection.is_empty:
        polys = None
        area = 0
    if intersection.geom_type == 'MultiPolygon':
        polys = list(intersection)
        area = reduce(lambda x,y: x.area + y.area, polys)
    elif intersection.geom_type == 'Polygon':
        polys =[ intersection ]
        area = intersection.area
    print("Before: ", polys)
    return_polys = list(map(getCoords, polys))
    print("After: ", return_polys)
    print("Area:", area)
    return return_polys

def main():
    pg.init()
    WHITE = (255, 255, 255)
    BLACK = (0,0,0)

    screen = pg.display.set_mode((1440, 800), 0, 32)
    screen.fill(WHITE)
    pg.display.set_caption("ScratchBoard")

    clock = pg.time.Clock()
    color = pg.Color('dodgerblue1')

    polys = []
    #polys = [(385, 256), (369, 295), (224, 308), (178, 502), (372, 637),
    #          (751, 616), (1005, 594), (1169, 569), (1186, 521), (1130, 456),
    #          (1029, 412), (990, 364), (1005, 309), (1102, 252), (1282,
    #          144), (1306, 99), (1271, 72), (468, 134), (414, 173)]
    track_outer = [(334, 215), (323, 237), (293, 248), (222, 255), (172, 270),
     (120, 403), (81, 506), (321, 730), (1248, 640), (1286, 588),
     (1274, 509), (1228, 459), (1179, 419), (1091, 377), (1063, 357),
     (1063, 341), (1100, 311), (1195, 273), (1307, 206), (1376, 140),
     (1379, 69), (1336, 23), (431, 79), (370, 114), (334, 215)]
    ob_bottom=[ (81, 506), (321, 730), (1248, 640), (1286, 588),
            (1274, 509), (1228, 459), (1179, 419), (1091, 377), (1063, 357),
            (1437, 328), (1436, 797), (0, 796), (0, 264), (172, 270) ]
    ob_top=[ (79, 505), (0, 505), (0, 0),(1438, 0),(1438, 505),
            (1179, 419), (1091, 377), (1063, 357),
            (1063, 341), (1100, 311), (1195, 273), (1307, 206), (1380, 140),
           (1380, 69), (1336, 23), (431, 79), (370, 114), (334, 215),
            (334, 215), (323, 237), (293, 248), (222, 255), (172, 270)]
    # Top is less than 390, bottom is greater than 390
    cutoff_point=390
    detection_zone=[ob_top, ob_bottom]
        #[ (79, 505), (1, 505), (1, 1),(1438, 1),(1438, 505),
        #    (1179, 419), (1091, 377), (1063, 357),
        #    (1063, 341), (1100, 311), (1195, 273), (1307, 206), (1376, 140),
        #   (1379, 69), (1336, 23), (431, 79), (370, 114), (334, 215),
        #    (334, 215), (323, 237), (293, 248), (222, 255), (172, 270)
        #]
    #detection_zone = [(79, 505), (0, 504), (0, 796), (1436, 797), (1437,
    # 328), (1064, 343)]


    #pg.draw.lines(screen, color, True, polys)
    #pg.draw.lines(screen, color, True, track_outer)
    for zone in detection_zone:
        pg.draw.polygon(screen, (0,0,0), zone)

    points=[]
    first_pos=None
    last_pos=None
    done = False
    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            elif event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = pg.mouse.get_pos()
                points.append(mouse_pos)
                if first_pos is None:
                    first_pos = mouse_pos
                if last_pos is not None:
                    last_pol = pg.math.Vector2(last_pos)
                    vect = (mouse_pos - last_pol).as_polar()
                    pg.draw.line(screen, BLACK, last_pos, mouse_pos, 1)
                    print (vect)
                pg.draw.circle(screen, color, mouse_pos, 5, 2)
                last_pos = mouse_pos
                print( "Click" )
            elif pg.key.get_pressed()[pg.K_SPACE]:
                if last_pos is not None and first_pos is not None:
                    last_pol = pg.math.Vector2(last_pos)
                    vect = (first_pos - last_pol).as_polar()
                    pg.draw.line(screen, BLACK, last_pos, first_pos, 1)
                    print(vect)

                if first_pos is None:
                    print("Skipping")
                else:
                    polys.append(points.copy())
                    points=[]
                    last_pos = None
                    first_pos = None
                    print("Reset")
                    for p in polys:
                        print(p)
            elif pg.key.get_pressed()[pg.K_DOWN]:
                if last_pos is not None and first_pos is not None:
                    last_pol = pg.math.Vector2(last_pos)
                    vect = (first_pos - last_pol).as_polar()
                    pg.draw.line(screen, BLACK, last_pos, first_pos, 1)
                    print(vect)

                if first_pos is None:
                    print("Skipping")
                else:
                    s = cliply(polys, points)[0]
                    over_points=[]
                    for x in s:
                        a, b = x
                        over_points.append((a,b))
                    points=[]
                    last_pos = None
                    first_pos = None
                    #print("Clipping Results")
                    #print(s)
                    print("Polys: ")
                    print(polys)
                    pg.draw.polygon(screen, color, s)



        pg.display.update()


if __name__ == '__main__':
    pg.init()
    main()
    pg.quit()
    sys.exit()