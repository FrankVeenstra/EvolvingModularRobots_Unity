from deap import base
from deap import tools
import multiprocessing
import numpy as np
from tqdm import tqdm
from emr.stats import statistics_logger
import os

# Example individual class with a fitness value and gene
class Individual:
    def __init__(self, controller_reference, fitness=0.0):
        self.controller = controller_reference()
        self.fitness = fitness
        self.limbs = [1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0]

    def save(self, path = None, name = None):
        self.controller.save_network(path, name)
        
    # def load(self,controller_reference, path = None, name = None):
    #     self.controller = controller_reference()
    #     self.controller.load_network(path,name)

    def load(self, path = None, name = None):
        self.controller.load_network(path, name)
    
    def generate_actions(self, j):
        return self.controller.step(None)

def custom_mutation(individual, mutation_rate : float = 0.1, sigma : float = 0.1, controller_mutation_rate : float = 0.1):
    individual.mutate(mutation_rate, sigma, controller_mutation_rate)
    
class EvolutionaryAlgorithm:
    def __init__(self, evaluation_function, config, individual_reference, controller_reference, n_cores : int = 1, run_number : int = 0, number_of_evaluation_steps : int = 500):
        # storing individual reference to get access to methods pertaining to the class
        self.individual_reference = individual_reference

        # Also store the evaluation function
        self.evaluation_function = evaluation_function
        self.run_number = run_number

        # number of cores to use
        self.n_cores = n_cores

        # task_id = self.run_number * self.n_cores

        mutation_prob = float(config['ea']['mutation_sigma'])
        mutation_sigma = float(config['ea']['mutation_prob'])
        morphmutation_prob = float(config['ea']['morphmutation_prob'])

        # ::::::::: Create Toolbox from DEAP ::::::::::
        toolbox = base.Toolbox()
        toolbox.register("individual",individual_reference, controller_reference, config)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate",evaluation_function, 
               executable_path=config['experiment']['executable_path'], 
               n_steps = number_of_evaluation_steps, scene_number_to_load = int(config['experiment']['scene_number']), 
                no_graphics = int(config['visualization']['headless']))
        #self.toolbox.register("mate", tools.cxTwoPoint) # disabled crossover
        
        # register mutation and selection
        toolbox.register("mutate", custom_mutation, mutation_rate=mutation_prob,sigma=mutation_sigma,controller_mutation_rate = morphmutation_prob)
        toolbox.register("select", tools.selTournament, tournsize=3)
        toolbox.register("selectBest", tools.selBest, fit_attr="fitness")
        toolbox.register("selectRandom", tools.selRandom)        

        self.toolbox = toolbox
        self.generation = 0
        self.experiment_path = config['experiment']['experiment_path']
        self.stats = statistics_logger.StatisticsLogger(experiment_path=self.experiment_path)
        if (not os.path.isdir(self.experiment_path)):
            os.makedirs(self.experiment_path,exist_ok=True)

    def print_stats(self):
        fits = self.stats.data[-1]
        length = len(self.pop)
        mean = sum(fits) / length
        sum2 = sum(x*x for x in fits)
        std = abs(sum2 / length - mean**2)**0.5
        print(f"Min {min(fits)}, max {max(fits)}, avg {mean}, std {std} ")
        

    def initialize(self,config):
        self.pop = self.toolbox.population(n=int(config['ea']['batch_size']))
        import emr.environment.evaluation as eval
        
        if (self.n_cores == 1):
            self.evaluate_population(self.pop)
            self.toolbox.register("close", eval.close_env)  
        else:
            pool = multiprocessing.Pool(self.n_cores)
            cs = int(np.ceil(float(len(self.pop)/float(self.n_cores))))
            # register the map function in toolbox, toolbox.map can be used to evaluate a population of len(pop)
            self.toolbox.register("map", pool.map, chunksize=cs)  
            #self.toolbox.register("close",self.toolbox.map(eval.close_env))
            self.toolbox.register("close", self.close_thread_pool, pool)  
            # evaluate the first individuals
            fits = self.toolbox.map(self.toolbox.evaluate, self.pop)
            for i, ind in enumerate(self.pop):
                ind.fitness = fits[i]

    def close_thread_pool(self,pool):
        pool.close()

    def run(self, config, n_generations):
        self.initialize(config)
        for _ in tqdm(range(n_generations), "Generation: "):
            self.epoch()
        self.toolbox.close()

    def epoch(self, elitism : int = 0, overlapping_generations = False):
        self.generation+=1

        # ::::::::: Parent Selection & Offspring Creation ::::::::::

        # Select the next generation individuals (elitism is done manually later)
        offspring = self.toolbox.select(self.pop, len(self.pop)-elitism)
        # Clone the selected individuals (deep copy)
        offspring = list(map(self.toolbox.clone, offspring))

        # ::::::::: Mutation ::::::::::
        for mutant in offspring:
            # TODO: Flag individuals when they are actually changed, no need to reevaluate indivuduals that haven't changed.
            self.toolbox.mutate(mutant)
            mutant.fitness = -2

        # ::::::::: Crossover ::::::::::
        # Not implemented right now
     
        # ::::::::: Evaluation of offspring ::::::::::      
        self.evaluate_population(offspring)

        # ::::::::: Elitism ::::::::::
        elites = []
        if elitism != 0:
            elites = self.toolbox.selectBest(self.pop, elitism)

        # ::::::::: Survivor Selection ::::::::::
        if (overlapping_generations == False):
            self.pop[:] = offspring + elites
        else:
            self.pop = self.toolbox.select(self.pop + offspring + elites, len(self.pop))
    
        # ::::::::: Logging ::::::::::
        fits = [ind.fitness for ind in self.pop]
        self.stats.append_data(fits)
        
        best_individual = self.toolbox.selectBest(self.pop, 1)
        self.individual_reference.save(best_individual,"",f"{self.experiment_path}i_{self.generation}")
        
    def evaluate_population(self,offspring):
        if (self.n_cores == 1):
            for ind in tqdm(offspring, desc="Evaluating Population"):
                if not ind.isDirty:
                    # No need to reevaluate individual that is not mutated
                    continue
                ind.fitness = self.toolbox.evaluate(ind)
            fits = [ind.fitness for ind in offspring]
        else:
            fits = self.toolbox.map(self.toolbox.evaluate, offspring)
            # Fitness stored in object used in thread not overriden, manual override here:
            for i in range(len(fits)):
                offspring[i].fitness = fits[i]
        return fits


    def load_best(self, config):
        import os
        last_ind_file_name = None
        last_ind = None
        executable_path = config['experiment']['executable_path']
        file_present= True
        count = 0
        while file_present:
            count+=1
            filename = f"{self.experiment_path}/i_{count}.pcl"
            if os.path.isfile(filename):
                last_ind_file_name = filename
            else:
                file_present = False
        if (last_ind_file_name == None):
            print(f"Didn't find an individual to load in {self.experiment_path}")
            return
        print(f"Loading {last_ind_file_name} ")
        last_ind = self.individual_reference.load("",last_ind_file_name)[0]
        for i in range(1):
            print(f"fitness used to be : {last_ind.fitness}")
            fit = self.evaluation_function(last_ind, executable_path, scene_number_to_load = int(config['experiment']['scene_number']))
            print(f"fitness : {fit}")
