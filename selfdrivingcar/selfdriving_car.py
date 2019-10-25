import sys
import pygame as pg
import matplotlib.path as mpltPath
import neat
import pickle


from selfdrivingcar.world.car import Car
from selfdrivingcar.helpers.geometery import *
from selfdrivingcar.world.track import *
from selfdrivingcar.ai.driver import RandomDriver, HumanDriver, NeatDriver

### GLOBALS ###
DODGER_BLUE = pg.Color('dodgerblue1')
RED = (220, 0, 0)
GREEN = (60, 220, 20)
WHITE = (255, 255, 255)

class ScoreBoard(pg.sprite.Sprite):
    def __init__(self, pos):
        ## Initialize
        super().__init__()
        # Two members required for a Sprite to draw itself- image, rect
        # Image defines the look
        # Rect defines the boundaries
        self.dimensions = (105, 103)
        self.image = pg.Surface(self.dimensions)
        self.rect = self.image.get_rect(center=pos)
        self.image.fill(WHITE)
        self.font = pg.font.Font('freesansbold.ttf', 32)
        self.header = self.font.render(' Score ', True, GREEN,
                                       DODGER_BLUE)
        self.image.blit(self.header,(0,0))
        self.score = 0
        self.idle_counter = 0
        self.distance = -1
        self.gameOver = False

    def update(self, new_dist = None):
        self.text = self.font.render("{0}".format(self.score),True,(0,0,0))
        if new_dist is not None:
            self.distance = new_dist
        dist = self.font.render("%.0f" % self.distance,True,(0,0,0))
        self.image.fill(WHITE)
        self.image.blit(self.header,(0,0))
        self.image.blit(self.text,(0,40))
        self.image.blit(dist,(0,75))
        #self.idle_counter += 1

        #if self.distance >= 200 or self.idle_counter > 400:
        if self.distance >= 200:
            self.gameOver = True


    def scoreInc(self, amount):
        self.score += amount
        self.idle_counter = 0

# TODO: Dying Logic: If Dist > 180, world dies
class Game:
    def __init__(self, network = None, genome = None):
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
        #self.driver = HumanDriver(self.player)
        self.driver = NeatDriver(self.player, network, genome)
        self.dead = False

        # Determine starting square:
        self.car_square, self.next_square= find_square_conatining(
            self.track_squares, self.player.pos)

    def run(self):
        while not self.exit:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.exit = True
            if self.score.gameOver or self.dead:
                self.screen.fill((30, 30, 30))
                self.text_sprites.draw(self.screen)
                self.exit = True

            keys, self.dead = self.driver.getMovement(self.score.score)
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
            next_goal=self.track_squares[self.next_square]
            # Sprites
            self.car_sprites.update(next_goal)
            self.text_sprites.update(d)
            self.screen.fill((30, 30, 30))
            for side in self.boundary:
                pg.draw.lines(self.screen, RED, False, side, 2)
            pg.draw.polygon(self.screen, GREEN,
                            self.track_squares[self.car_square])
            pg.draw.polygon(self.screen, RED,
                            self.track_squares[self.next_square])
            for gate in TRACK_GATES:
                pg.draw.line(self.screen, GREEN, gate[0], gate[1], 3)
            #for col in self.player.collisions:
                # Unpack position, collision, and distance
                #p, c, d = col
                #pg.draw.circle(self.screen, DODGER_BLUE, c, 5, 2)
                #pg.draw.line(self.screen, DODGER_BLUE, p, c, 2)
            self.car_sprites.draw(self.screen)
            self.text_sprites.draw(self.screen)

            pg.display.flip()
            self.clock.tick(30)
        #pg.display.quit()
        pg.quit()



def eval_genomes(genomes, config):
    #genome_id, genome = genomes[0]
    for genome_id, genome in genomes:
        net = neat.nn.recurrent.RecurrentNetwork.create(genome, config)
        game = Game(net, genome)
        game.run()
        print("Finished: ", genome_id, genome.fitness)

def main():
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         'NEAT_Car.conf')

    p = neat.Population(config)
    print(p)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(10))

    winner = p.run(eval_genomes)
    print(winner)
    # pickel the output to store the network
    with open('winner.pkl', 'wb') as output:
        pickle.dump(winner, output, 1)

if __name__ == '__main__':
    #game = Game()
    #game.run()
    main()
    sys.exit()