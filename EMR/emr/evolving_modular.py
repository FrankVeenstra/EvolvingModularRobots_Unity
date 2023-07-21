import mlagents_envs as envs

import numpy as np
import random
from emr.encoding import LSystem
from emr.encoding import direct_encoding
from emr.controller import custom_controller
from emr.controller import phase_coupled_oscillator as pco
from emr.environment import evaluation as ev
from tqdm import tqdm

from evolution import deap_interface
from encoding import LSystem
from config import config_handler

#import evolution as ea

POPULATION_SIZE = 10

	
def evolve_deap(config):
	# TODO Extend the functionality for some general purpose argument parsing
	exp_path, run_number, n_cores, mutation_rate, n_generations = config_handler.get_arguments_from_parser()
	config['experiment']['experiment_path'] = "exp0/"
	config['visualization']['headless'] = '0'

	if (mutation_rate != None):
		config['experiment']['morphmutation_prob'] = mutation_rate

	# temp -------------
	n_cores = 1
	run_number = 4
	# ------------------

	# The Evolutionary Algorithm code can be a little bit tricky to understand, hopefully this will clarify it:
	"""
	get_env: singleton for getting an environment (making sure only one environment is open per core)
	evaluation_function: reference to the evaluation function (handling interaction with unity, returning fitness value)
	config: the config file used
	individual_reference: Reference to the encoding to use (Now supports [1] DirectEncoding.DirectEncoding [2] LSystem.GraphGrammar)
	controller_reference: Reference to the controller to use (per module)
	(optional) n_cores:  Number of cores
	(optional) mutation_rate: for setting the mutation_rate quickly with arguments	
	"""
	use_lystem = True
	if (use_lystem):
		ea = deap_interface.EvolutionaryAlgorithm(ev.evaluate_individual, config, 
			LSystem.GraphGrammar, pco.PhaseCoupledOscillator, n_cores = int(n_cores), 
			run_number = int(run_number))
	else:
		ea = deap_interface.EvolutionaryAlgorithm(ev.evaluate_individual, config, 
			direct_encoding.DirectEncoding, custom_controller.Controller,n_cores = int(n_cores), 
			run_number = int(run_number))
	
	# Random seed set for both numpy and random just to be sure it's deterministic
	np.random.seed(int(run_number))
	random.seed(int(run_number))

	# Initialize the EA
	ea.initialize(config)

	# Run the EA for n_generations
	for _ in tqdm(range(n_generations)):
		ea.epoch()
		ea.stats.save(filename = "stats")
		ea.print_stats()

	# Uncomment below to load the best individual
	# ea.load_best()
	return ea

def load_best_individual(config):
	exp_path, run_number, n_cores, mutation_rate, n_generations = config_handler.get_arguments_from_parser()
	config['visualization']['headless'] = '0'
	ea = deap_interface.EvolutionaryAlgorithm(ev.evaluate_individual, config, 
			LSystem.GraphGrammar, pco.PhaseCoupledOscillator,n_cores = 1, 
			run_number = int(run_number))
	print("Loading Best")
	ea.load_best(config)

def evolve_nsga2(config):
	from ea import nsga2
	exp_path, run_number, n_cores = get_arguments_from_parser()
	n_cores = "4"
	# ea = nsga2.NSGA2(ev.get_env, ev.evaluate_individual_multi_objective, LSystem.GraphGrammar, custom_controller.Controller
	#	, experiment_path=exp_path + "/", n_cores = int(n_cores), run_number = int(run_number))
	ea = nsga2.NSGA2(ev.get_env, ev.evaluate_individual_multi_objective, DirectEncoding.DirectEncoding, custom_controller.Controller
		, experiment_path=exp_path + "/", n_cores = int(n_cores), run_number = int(run_number))
	np.random.seed(int(run_number))
	random.seed(int(run_number))
	ea.reset(POPULATION_SIZE)
	for _ in range(200):
		ea.step()
		ea.stats.save(filename = "stats")
	#load_best(ea=ea)
	return ea

if __name__ == "__main__":
	from config import config_handler
	config = config_handler.make_config()
	""" 
	The evaluation.py file contains code pertaining to the interface with Unity. 
	Specifically look at the get_env function that you can call in editor mode or not. 
	"""
	# load_best_individual(config)
	ea = evolve_deap(config)

	# A few things I was working on, don't worry about this. NSGA2 might not be fully working
	#save_jsonfile()
	#run_multithreaded()
	#test_save_load()
	#ea = evolve_nsga2(config)

