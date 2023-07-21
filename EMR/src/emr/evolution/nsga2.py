# import array
# import json
# import numpy

import multiprocessing
import random

from math import sqrt
from deap import base, tools, algorithms
from deap.benchmarks.tools import diversity, convergence, hypervolume

toolbox = base.Toolbox()

from stats import StatisticsLogger
import ea.deap_interface
import os
from tqdm import tqdm
import numpy as np

from deap import creator


class _Fitness(base.Fitness):
    weights = (1.,1.)
    
class NSGA2:
    def __init__(self, get_env, evaluation_function, config, individual_reference, controller_reference, n_cores : int = 1, run_number : int = 0, mutation_rate : float = None):
        self.createEnv = get_env
        self.evaluation_function = evaluation_function  # reference to the evaluation function
        self.individual_reference = individual_reference
        self.run_number = run_number
        self.n_cores = n_cores
        self.socket_number_offset = int(self.run_number * self.n_cores)
        toolbox = base.Toolbox()
        toolbox.register("fit", _Fitness)
        toolbox.register("individual",individual_reference, controller_reference, config, fitness=toolbox.fit())
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate",evaluation_function)
        if (mutation_rate != None):
            toolbox.register("mutate", ea.deap_interface.custom_mutation, mutation_rate=mutation_rate,sigma=ea.deap_interface.MUTATION_SIGMA,controller_mutation_rate = mutation_rate)
        else:
            toolbox.register("mutate", ea.deap_interface.custom_mutation, mutation_rate=ea.deap_interface.MUTATION_PROBABILITY,sigma=ea.deap_interface.MUTATION_SIGMA,controller_mutation_rate = ea.deap_interface.CONTROLLER_MUTATION_PROBABILITY)
        toolbox.register("select", tools.selNSGA2)
        toolbox.register("select_best", tools.selBest, fit_attr="fitness")
        toolbox.register("select_random", tools.selRandom)
        self.toolbox = toolbox
        self.generation = 0
        self.experiment_path = config['experiment']['experiment_path']
        self.stats = StatisticsLogger.StatisticsLogger(experiment_path=self.experiment_path)
        if (not os.path.isdir(self.experiment_path)):
            os.makedirs(self.experiment_path,exist_ok=True)
        
        # make sure population size % 4 
        # = 0  TODO

    def step(self, elitism : int = 1):
        self.generation+=1
        # Select the next generation individuals
        offspring = tools.selTournamentDCD(self.pop, len(self.pop))
        # Clone the selected individuals
        offspring = list(map(self.toolbox.clone, offspring))

        for mutant in offspring:
            self.toolbox.mutate(mutant)

        
        # Evaluate new population
        self.evaluate_population()  
        fits = [ind.fitness.values[0] for ind in self.pop]
        self.pop = self.toolbox.select(self.pop + offspring, len(self.pop)) 
    
        length = len(self.pop)
        mean = sum(fits) / length
        sum2 = sum(x*x for x in fits)
        std = abs(sum2 / length - mean**2)**0.5

        # duplicated code for saving elite
        elite = self.toolbox.select_best(self.pop, 1)[0]
        self.individual_reference.save(elite,"",f"{self.experiment_path}i_{self.generation}")

        self.stats.append_data(fits)
        print(f"Min {min(fits)}, max {max(fits)}, avg {mean}, std {std} ")

    def evaluate_population(self):
        fits = self.toolbox.map(self.toolbox.evaluate, self.pop)
        for ind, fit in zip(self.pop, fits):
            ind.fitness.values = fit

    

    def uniform(low, up, size=None):
        try:
            return [random.uniform(a, b) for a, b in zip(low, up)]
        except TypeError:
            return [random.uniform(a, b) for a, b in zip([low] * size, [up] * size)]

    # toolbox.register("attr_float", uniform, BOUND_LOW, BOUND_UP, NDIM)
    # toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.attr_float)
    # toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    # toolbox.register("evaluate", benchmarks.zdt1)
    # toolbox.register("mate", tools.cxSimulatedBinaryBounded, low=BOUND_LOW, up=BOUND_UP, eta=20.0)
    # toolbox.register("mutate", tools.mutPolynomialBounded, low=BOUND_LOW, up=BOUND_UP, eta=20.0, indpb=1.0/NDIM)
    # toolbox.register("select", tools.selNSGA2)
    def reset(self, population_size):
        assert population_size % 4 == 0, "NSGAII requires population size multiple of 4, was: {:d}".format(population_size)
        self.pop = self.toolbox.population(n=population_size)
        if (self.n_cores == 1):
            self.evaluate_population()
        else:
            pool = multiprocessing.Pool(self.n_cores)
            cs = int(np.ceil(float(len(self.pop)/float(self.n_cores))))
            # register the map function in toolbox, toolbox.map can be used to evaluate a population of len(pop)
            self.toolbox.register("map", pool.map, chunksize=cs)  
            # evaluate the first individuals
            self.evaluate_population()
        # to set crowding distance, no actual selection is done
        self.pop = self.toolbox.select(self.pop, len(self.pop))

    def load_best(self):
        import os
        last_ind_file_name = None
        last_ind = None
        
        for i in range(100):
            filename = f"{self.experiment_path}/i_{i}.pcl"
            if os.path.isfile(filename):
                last_ind_file_name = filename
        last_ind = self.individual_reference.load("",last_ind_file_name)
        for i in range(2):
            fit = self.evaluation_function(last_ind)
            print(f"fitness : {fit}")

    def getBestIndividual(self):
        sorted_pop = sorted(self.pop[:], key=lambda ind: ind.fitness, reverse=True)
        return sorted_pop[0] # best individual


#Below is for reference. e.g. hypervolume plotting

    def main(seed=None):
        random.seed(seed)

        NGEN = 250
        MU = 100
        CXPB = 0.9
        from deap import benchmarks
        toolbox.register("evaluate", benchmarks.zdt1)

        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", numpy.mean, axis=0)
        stats.register("std", numpy.std, axis=0)
        stats.register("min", numpy.min, axis=0)
        stats.register("max", numpy.max, axis=0)

        logbook = tools.Logbook()
        logbook.header = "gen", "evals", "std", "min", "avg", "max"

        pop = toolbox.population(n=MU)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in pop if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # This is just to assign the crowding distance to the individuals
        # no actual selection is done
        pop = toolbox.select(pop, len(pop))

        record = stats.compile(pop)
        logbook.record(gen=0, evals=len(invalid_ind), **record)
        print(logbook.stream)

        # Begin the generational process
        for gen in range(1, NGEN):
            # Vary the population
            offspring = tools.selTournamentDCD(pop, len(pop))
            offspring = [toolbox.clone(ind) for ind in offspring]

            for ind1, ind2 in zip(offspring[::2], offspring[1::2]):
                if random.random() <= CXPB:
                    toolbox.mate(ind1, ind2)

                toolbox.mutate(ind1)
                toolbox.mutate(ind2)
                del ind1.fitness.values, ind2.fitness.values

            # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            # Select the next generation population
            pop = toolbox.select(pop + offspring, MU)
            record = stats.compile(pop)
            logbook.record(gen=gen, evals=len(invalid_ind), **record)
            print(logbook.stream)

        print("Final population hypervolume is %f" % hypervolume(pop, [11.0, 11.0]))

        return pop, logbook

if __name__ == "__main__":
    #with open("pareto_front/zdt1_front.json") as optimal_front_data:
    #    optimal_front = json.load(optimal_front_data)
    # Use 500 of the 1000 points in the json file
    #optimal_front = sorted(optimal_front[i] for i in range(0, len(optimal_front), 2))

    pop, stats = NSGA2.main()
    pop.sort(key=lambda x: x.fitness.values)

    print(stats)
    #print("Convergence: ", convergence(pop, optimal_front))
    #print("Diversity: ", diversity(pop, optimal_front[0], optimal_front[-1]))

    import matplotlib.pyplot as plt
    import numpy

    front = numpy.array([ind.fitness.values for ind in pop])
    #optimal_front = numpy.array(optimal_front)
    #plt.scatter(optimal_front[:,0], optimal_front[:,1], c="r")
    plt.scatter(front[:,0], front[:,1], c="b")
    plt.axis("tight")
    plt.show()
