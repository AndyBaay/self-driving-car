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
        self.text_sprites = pg.sprite.Group()
        self.race_track = MonzoTrack(1440,880)

        self.cars = ["Renault_1", "Renault_2", "Renault_3", "Renault_4"]
        self.player = Car("Renault_0", (946, 74), self.race_track)
        self.score = ScoreBoard((80,60))
        self.car_sprites.add(self.player)
        self.text_sprites.add(self.race_track)
        self.driver = HumanDriver(self.player)
        #self.driver = NeatDriver(self.player, network, genome)

        for car_name in self.cars:
            self.car_sprites.add(Car(car_name, (946, 74), self.race_track))

    def run(self):
        while not self.exit:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.exit = True

            keys = self.driver.getMovement(self.score.score)

            self.car_sprites.update(keys)
            self.text_sprites.update()
            #for col in self.player.collisions:
                # Unpack position, collision, and distance
                #p, c, d = col
                #pg.draw.circle(self.screen, DODGER_BLUE, c, 5, 2)
                #pg.draw.line(self.screen, DODGER_BLUE, p, c, 2)
            self.text_sprites.draw(self.screen)
            self.car_sprites.draw(self.screen)

            pg.display.flip()
            self.clock.tick(30)
        pg.quit()



#def eval_genomes(genomes, config):
    #genome_id, genome = genomes[0]
    #for genome_id, genome in genomes:
    #    net = neat.nn.recurrent.RecurrentNetwork.create(genome, config)
    #    game = Game(net, genome)
    #    game.run()
    #    print("Finished: ", genome_id, genome.fitness)

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
    game = Game()
    game.run()
    #main()
    sys.exit()