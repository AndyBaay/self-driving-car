import pygame, os
from pygame.locals import *

import math


def getAngle(a, b, c):
    ang = math.degrees(
        math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1],
                                                          a[0] - b[0]))
    return ang + 360 if ang < 0 else ang

def main():
    pygame.init()

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    mouse_position = (0, 0)
    drawing = False
    screen = pygame.display.set_mode((600, 800), 0, 32)
    screen.fill(WHITE)
    pygame.display.set_caption("ScratchBoard")

    position_array=[]
    last_pos = None
    first_position = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEMOTION:
                if (drawing):
                    mouse_position = pygame.mouse.get_pos()
                    if last_pos is not None:
                        pygame.draw.line(screen, BLACK, last_pos, mouse_position, 1)
                    last_pos = mouse_position
                    position_array.append(last_pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_position = (0, 0)
                drawing = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if first_position is None:
                    first_position = pygame.mouse.get_pos()
                drawing = True
            elif pygame.key.get_pressed()[pygame.K_SPACE]:
                if last_pos is not None:
                    pygame.draw.line(screen, BLACK, last_pos, first_position, 1)
                    last_pos=first_position
                    position_array.append(last_pos)
                    last_pos = None
                    first_position = None
            elif pygame.key.get_pressed()[pygame.K_DOWN]:
                print(first_position)
                print( position_array )

        pygame.display.update()

if __name__ == "__main__":
    main()