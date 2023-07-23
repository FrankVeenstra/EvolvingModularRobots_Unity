import numpy as np
import random
import sys
import os

from emr.encoding import graph_grammar, direct_encoding 
from emr.controller import custom_controller, phase_coupled_oscillator 
from emr.config import config_handler, config_utility
from emr.evolution import deap_interface as di
from emr.environment import evaluation
from emr import encoding

def load_best_saved_individual(config, experiment_path : str, ind_ref):
    import os
    last_ind_file_name = None
    last_ind = None
    executable_path = config['experiment']['executable_path']
    number_of_evaluation_steps = int(config['environment']['evaluation_steps'])
    import emr.environment.evaluation as evaluation

    file_present= True
    count = 0
    while file_present:
        count+=1
        filename = os.path.join(experiment_path,  f"i_{count}.pcl")
        if os.path.isfile(filename):
            last_ind_file_name = filename
        else:
            file_present = False
    if (last_ind_file_name == None):
        print(f"Didn't find an individual to load in {experiment_path}")
        return
    print(f"Found {last_ind_file_name} ")
    last_ind = ind_ref.load("",last_ind_file_name)[0]
    return last_ind, count

def load_individual(config, experiment_path : str, individual_number : int, ind_ref):
    import os
    last_ind_file_name = None
    last_ind = None
    executable_path = config['experiment']['executable_path']
    number_of_evaluation_steps = int(config['environment']['evaluation_steps'])
    import emr.environment.evaluation as evaluation
 
    filename = os.path.join(experiment_path,  f"i_{str(individual_number)}.pcl")
    if os.path.isfile(filename):
        last_ind_file_name = filename
    else:
        print(f"Didn't find an individual to load in {experiment_path}")
        file_present = False
        return None
    print(f"Found {last_ind_file_name} ")
    last_ind = ind_ref.load("",last_ind_file_name)[0]
    return last_ind, individual_number

def load_best(experiment_path : str, executable_path : str = "./EMR_Executable/EvolvingModularRobots"):
    print(f"Loading configuration from {experiment_path}")
    path = os.path.join(experiment_path, "config.cfg")
    if not os.path.isfile(path):
        print(f"Could not find config file here {path}")
        return
    # load experiment config 
    cfg = config_handler.load_config(path)
    config_handler.print_config(cfg)
    encoding, controller, evaluation_function = config_utility.get_encoding_controller_and_evaluation_from_config(cfg)
    modules_to_use = config_handler.modules_to_use(cfg)

    ea = di.EvolutionaryAlgorithm(evaluation_function, cfg, encoding, controller, modules_to_use)
    # load specific individual
    individual, number = load_best_saved_individual(cfg, experiment_path, encoding)

    n_steps = int(cfg['environment']['evaluation_steps'])

    print(f"Evaluating individual {individual} that had a fitness of {individual.fitness}")
    fitness = evaluation.evaluate_individual(individual, executable_path, n_steps = n_steps,scene_number_to_load = int(cfg['experiment']['scene_number']), editor_mode = False, no_graphics = False, record = False)
    print(f"fitness was : {fitness}")
    evaluation.env.reset()

if __name__ == "__main__":
    load_best(experiment_path = "./exp0")
    