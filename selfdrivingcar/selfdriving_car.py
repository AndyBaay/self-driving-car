import sys
import pygame as pg
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
        self.world_sprites = pg.sprite.Group()
        self.race_track = MonzoTrack(1440,880)

        #self.cars = ["Renault_1", "Renault_2", "Renault_3", "Renault_4"]
        #self.player = Car("Renault_0", (946, 74), self.race_track)
        self.score = ScoreBoard((80,60))
        #self.car_sprites.add(self.player)
        self.world_sprites.add(self.race_track)
        #self.driver = HumanDriver(self.player)
        #self.driver = NeatDriver(self.player, network, genome)

        self.to_be_removed = []

        #for car_name in self.cars:
        #    self.car_sprites.add(Car(car_name, (946, 74), self.race_track))

    def add_car(self, car):
        self.car_sprites.add(car)

    def run(self):
        while not self.exit:
            # Remove any dead sprites
            for s in self.to_be_removed:
                print(s.name, "scored", s.score)
                self.car_sprites.remove(s)
            self.to_be_removed = []

            self.check_game_over(pg.event.get())

            #keys = self.driver.getMovement(self.score.score)
            #self.car_sprites.update(keys)

            self.car_sprites.update()
            self.world_sprites.update()

            for sprite in self.car_sprites.sprites():
                if not sprite.alive:
                    self.to_be_removed.append(sprite)
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
    genome_id, genome = genomes[0]
    for genome_id, genome in genomes:
        c = Car("Renault_" + str(genome_id), (946, 74), game.race_track)
        net = neat.nn.recurrent.RecurrentNetwork.create(genome, config)
        driver= NeatDriver(net, genome)
        c.add_driver(driver)
        game.add_car(c)
    game.run()
    #print("Renault_" + str(genome_id), "scored", genome.fitness)

def main():
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
    # pickel the output to store the network
    with open('winner.pkl', 'wb') as output:
        pickle.dump(winner, output, 1)

if __name__ == '__main__':
    #game = Game()
    #game.run()
    main()
    sys.exit()