import sys
import pygame as pg
import neat
import pickle

from selfdrivingcar.world.car import Car
from selfdrivingcar.world.track import *
from selfdrivingcar.ai.driver import RandomDriver, HumanDriver, NeatDriver

### GLOBALS ###
DODGER_BLUE = pg.Color('dodgerblue1')
RED = (220, 0, 0)
GREEN = (60, 220, 20)
WHITE = (255, 255, 255)

# TODO Remove ScoreBoard or get font working that does not cause segmentation
#  fault
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

        self.score = 0
        self.idle_counter = 0
        self.distance = -1
        self.gameOver = False

    def update(self, new_dist = None):
        #self.text = self.font.render("{0}".format(self.score),True,(0,0,0))
        if new_dist is not None:
            self.distance = new_dist
        #dist = self.font.render("%.0f" % self.distance,True,(0,0,0))
        self.image.fill(WHITE)
        #self.image.blit(self.header,(0,0))
        #self.image.blit(self.text,(0,40))
        #self.image.blit(dist,(0,75))
        #self.idle_counter += 1

        #if self.distance >= 200 or self.idle_counter > 400:
        if self.distance >= 120:
            self.gameOver = True


    def scoreInc(self, amount):
        self.score += amount
        self.idle_counter = 0

# TODO: Dying Logic: If Dist > 180, world dies
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

        self.score = ScoreBoard((80,60))

        self.car_sprites = pg.sprite.Group()

        self.world_sprites = pg.sprite.Group()
        self.race_track = MonzoTrack(1440,880)
        self.world_sprites.add(self.race_track)

        self.cars_to_remove = []

    def add_car(self, car):
        self.car_sprites.add(car)

    def run(self):
        while not self.exit:
            # Remove any dead sprites
            for s in self.cars_to_remove:
                print(s.name, "scored", s.score)
                self.car_sprites.remove(s)
            self.cars_to_remove = []

            self.check_game_over(pg.event.get())

            self.car_sprites.update()
            self.world_sprites.update()

            for sprite in self.car_sprites.sprites():
                if not sprite.alive:
                    self.cars_to_remove.append(sprite)
            self.world_sprites.draw(self.screen)
            self.car_sprites.draw(self.screen)

            pg.display.flip()
            self.clock.tick(30)
        pg.quit()

    def check_game_over(self, events):
        # Check if the player manually exited
        for event in events:
            if event.type == pg.QUIT:
                self.exit = True

        # Check if all the cars are dead
        if len(self.car_sprites.sprites()) == 0 :
            print("No sprites found")
            self.exit = True


def eval_genomes(genomes, config):
    game = Game()
    for genome_id, genome in genomes:
        car = Car("Renault_" + str(genome_id), (946, 74), game.race_track)
        net = neat.nn.recurrent.RecurrentNetwork.create(genome, config)
        driver = NeatDriver(car, net, genome)
        car.add_driver(driver)
        game.add_car(car)
    game.run()
    print("Renault_" + str(genome_id), "scored", genome.fitness)


def main(test = False):

    if test:
        game = Game()
        car = Car("Renault_Tester", (946, 74), game.race_track)
        driver = HumanDriver(car)
        car.add_driver(driver)
        game.add_car(car)
        game.run()
        return

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         'NEAT_Car.conf')

    p = neat.Population(config)
    #p = neat.Checkpointer.restore_checkpoint(
    #    "../states/first_success/neat-checkpoint-216")

    print(p)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(10))


    winner = p.run(eval_genomes)
    print(winner)
    with open('winner.pkl', 'wb') as output:
        pickle.dump(winner, output, 1)

if __name__ == '__main__':
    #main(test = True)
    main()
    sys.exit()