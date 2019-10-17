import numpy as np
import cv2
import neat
import pickle


# Call this to evaluate all the genomes
def eval_genomes(genomes, config):

    # For just a single genome, test it like this (i.e. one iteration of the
    # game)
    for genome_id, genome in genomes:

        net = neat.nn.recurrent.RecurrentNetwork.create(genome, config)

        current_max_fitness = 0
        fitness_current = 0
        frame = 0
        counter = 0

        done = False

        # On each iteration of frames
        while not done:

            # Feed sensor data in, store the output
            nnOutput = net.activate(imgarray)

            # Turn off the feedback loop for now
            #ob, rew, done, info = env.step(nnOutput)

            #fitness_current += rew

            #if fitness_current > current_max_fitness:
            #    current_max_fitness = fitness_current
            #    counter = 0
            #else:
            #    counter += 1

            if done or counter == 250:
                done = True
                print(genome_id, fitness_current)

            genome.fitness = fitness_current


config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     'config-feedforward')

p = neat.Population(config)

p.add_reporter(neat.StdOutReporter(True))
stats = neat.StatisticsReporter()
p.add_reporter(stats)
p.add_reporter(neat.Checkpointer(10))

winner = p.run(eval_genomes)

# pickel the output to store the network
with open('winner.pkl', 'wb') as output:
    pickle.dump(winner, output, 1)