import pygame, os

import math


def getAngle(a, b, c):
    ang = math.degrees(
        math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1],
                                                          a[0] - b[0]))
    return ang + 360 if ang < 0 else ang

def makeObtuse(a):
    return 360 - a

def splitAngles(a):
    return float(a) / 2.0

def getNewPoint((x1,y1),angle, line_length):
    return (x1 + line_length * cos(angle), y1 + line_length * sin(angle))


def main():
    points = [(0,0), (0,1), (6,0)]
    points_len = len(points)
    loop = range(len(points))
    angles = []

    for p in loop:
        first = (p - 1) % points_len
        second = (p) % points_len
        third = (p + 1) % points_len
        angles.append( getAngle(points[first], points[second], points[third]) )

    final_angles = []
    if sum(angles) < len(angles) * 180:
        final_angles = map(makeObtuse, angles)
    else:
        final_angles = angles

    print angles
    print final_angles
    print map(splitAngles, final_angles)

    print ((0,0), )

    print points
if __name__ == "__main__":
    main()