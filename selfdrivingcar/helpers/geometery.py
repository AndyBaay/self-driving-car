import math
from functools import reduce
from shapely.geometry import Polygon, Point, LinearRing

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

def find_square_conatining (squares, pos, checking_square = 0,
                            squares_lookahead = None):
    if squares_lookahead is None: squares_lookahead = len(squares)
    found_square=None
    while found_square is None and squares_lookahead > 0:
        sqr = Polygon(squares[checking_square])
        pt = Point(pos)
        inside2 = sqr.contains(pt)
        if inside2:
            found_square = checking_square
            return found_square, (found_square + 1) % len(squares)
        checking_square = (checking_square + 1) % len(squares)
        squares_lookahead -= 1
    return found_square, None

## Finding overlap of polygons
def getCoords(polygon: Polygon):
    return list(polygon.exterior.coords)

# Returns the overlaping polygon coordinates and total area of overlap
def findOverlap(p1, p2):
    a= Polygon(p1[0])
    b= Polygon(p2)
    intersection= a.intersection(b)

    if not intersection.is_empty:
        polys = None
        return [], 0
    if intersection.geom_type == 'MultiPolygon':
        polys = list(intersection)
        area = reduce(lambda x,y: x.area + y.area, polys)
    elif intersection.geom_type == 'Polygon':
        polys =[ intersection ]
        area = intersection.area

    return_polys = list(map(getCoords, polys))
    return return_polys, area