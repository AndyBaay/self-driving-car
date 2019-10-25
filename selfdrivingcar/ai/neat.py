import numpy as np
import neat
import pickle
from selfdrivingcar.selfdriving_car import Game


# Call this to evaluate all the genomes
def eval_genomes(genomes, config):

    # For just a single genome, test it like this (i.e. one iteration of the
    # game)
    #for genome_id, genome in genomes:
    genome_id, genome = genomes[0]

    net = neat.nn.recurrent.RecurrentNetwork.create(genome, config)

    current_max_fitness = 0
    fitness_current = 0
    frame = 0
    counter = 0

    done = False

    game = Game(net)
    game.run()

    # On each iteration of frames
    #while not done:

        # Feed sensor data in, store the output
        #nnOutput = net.activate(imgarray)

        # Turn off the feedback loop for now
        #ob, rew, done, info = env.step(nnOutput)

        #fitness_current += rew

        #if fitness_current > current_max_fitness:
        #    current_max_fitness = fitness_current
        #    counter = 0
        #else:
        #    counter += 1

        #if done or counter == 250:
        #    done = True
        #    print(genome_id, fitness_current)

        #genome.fitness = fitness_current
