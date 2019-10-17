import pygame as pg
from pygame.math import Vector2


def draw_line(position, angle, line_length, line_width, color, screen):
    vector = Vector2()  # A zero vector.
    vector.from_polar((line_length, angle))  # Set the desired length and angle of the vector.
    # Add the vector to the `position` to get the second point.
    pg.draw.line(screen, color, position, position+vector, line_width)


pg.init()
screen = pg.display.set_mode((640, 480))
clock = pg.time.Clock()
BG_COLOR = pg.Color('gray13')
BLUE = pg.Color('dodgerblue1')

done = False
while not done:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True

    screen.fill(BG_COLOR)
    draw_line((100, 200), 30, 120, 2, BLUE, screen)
    draw_line((100, 200), -90, 120, 2, BLUE, screen)
    pg.display.flip()
    clock.tick(30)

pg.quit()