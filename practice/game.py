import os
import pygame
from math import sin, radians, degrees, copysign
from pygame.math import Vector2


class Car:
    def __init__(self, x, y, angle=0.0, length=4, max_steering=75,
                 max_acceleration=25.0):
        self.position = Vector2(x, y)
        self.velocity = Vector2(0.0, 0.0)
        self.angle = angle
        self.length = length
        self.max_acceleration = max_acceleration
        self.max_steering = max_steering
        self.max_velocity = 20
        self.brake_deceleration = 30
        self.free_deceleration = 2

        self.acceleration = 0.0
        self.steering = 0.0

    def update(self, dt):
        self.velocity += (self.acceleration * dt, 0)
        self.velocity.x = max(-self.max_velocity, min(self.velocity.x, self.max_velocity))
        #self.detectCollision()

        if self.steering:
            turning_radius = self.length / sin(radians(self.steering))
            angular_velocity = self.velocity.x / turning_radius
        else:
            angular_velocity = 0

        self.position += self.velocity.rotate(-self.angle) * dt
        self.angle += degrees(angular_velocity) * dt

    def detectCollision(self):

        if self.position.x > 30:
            print( "Collision: True" )
        else:
            print( "Collision: False" )


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Car tutorial")
        width = 1280
        height = 720
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.ticks = 60
        self.exit = False

    def run(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print(current_dir)
        image_path = os.path.join("/Users/andybaay/Developer/car-ai/pygame-car-tutorial", "assets/McLaren_Racer.png")
        print(image_path)
        car_image = pygame.image.load(image_path)
        car = Car(10, 10)
        ppu = 32

        while not self.exit:
            dt = self.clock.get_time() / 1000

            # Event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            # User input
            pressed = pygame.key.get_pressed()

            if pressed[pygame.K_UP]:
                if car.velocity.x < 0:
                    car.acceleration = car.brake_deceleration
                else:
                    car.acceleration += 8 * dt
            elif pressed[pygame.K_DOWN]:
                if car.velocity.x > 0:
                    car.acceleration = -car.brake_deceleration
                else:
                    car.acceleration -= 8 * dt
            elif pressed[pygame.K_SPACE]:
                if abs(car.velocity.x) > dt * car.brake_deceleration:
                    car.acceleration = -copysign(car.brake_deceleration, car.velocity.x)
                else:
                    car.acceleration = -car.velocity.x / dt
            else:
                if abs(car.velocity.x) > dt * car.free_deceleration:
                    car.acceleration = -copysign(car.free_deceleration, car.velocity.x)
                else:
                    if dt != 0:
                        car.acceleration = -car.velocity.x / dt
            car.acceleration = max(-car.max_acceleration, min(car.acceleration, car.max_acceleration))

            if pressed[pygame.K_RIGHT]:
                car.steering -= 300 * dt
            elif pressed[pygame.K_LEFT]:
                car.steering += 300 * dt
            else:
                car.steering = 0
            car.steering = max(-car.max_steering, min(car.steering, car.max_steering))

            # Logic
            car.update(dt)

            # Drawing
            self.screen.fill((0, 0, 0))
            pygame.draw.rect(self.screen, (100,100,100), (10, 5, 200, 10))
            self.draw_a_tree(150,(400,300))
            rotated = pygame.transform.rotate(car_image, car.angle)
            rect = rotated.get_rect()
            self.screen.blit(rotated, car.position * ppu - (rect.width / 2, rect.height / 2))
            pygame.display.flip()

            self.clock.tick(self.ticks)
        pygame.quit()

    def draw_a_tree(self, leaf_size, tup, is_trunk=True):
        x, y = tup
        if is_trunk:
            rect = pygame.rect.Rect((x - 25, y - 30), (50,60))
            pygame.draw.rect(self.screen, (102,68,34), rect)
            self.draw_a_tree(leaf_size, (x, y-30), False)
        elif leaf_size <= 2:
            return
        else:
            pygame.draw.polygon(self.screen, (0,200,0),((x-leaf_size/2,y),
                                              (x+leaf_size/2,y),(x,y-(2*leaf_size/3))))
            self.draw_a_tree(3*leaf_size/4, (x, y-leaf_size/3), False)

    def draw_our_track(self):
        COORDS = [(468, 99), (772, 104), (820, 111), (841, 121), (856, 141), (866, 164), (869, 186), (869, 212), (871, 227), (879, 232), (890, 233), (910, 235), (925, 236), (942, 242), (949, 254), (950, 266), (949, 278), (945, 296), (935, 308), (916, 312), (896, 312), (874, 311), (196, 210), (188, 196), (188, 173), (192, 157), (204, 133), (230, 118), (256, 108), (308, 100), (466, 102)]
[(315, 134), (768, 137), (788, 139), (797, 145), (804, 152), (809, 159), (814, 169), (816, 181), (818, 192), (818, 205), (818, 219), (820, 232), (824, 242), (832, 249), (849, 260), (863, 265), (876, 269), (888, 271), (896, 271), (902, 273), (894, 276), (245, 177), (245, 165), (256, 156), (279, 145)]



if __name__ == '__main__':
    game = Game()
    game.run()
