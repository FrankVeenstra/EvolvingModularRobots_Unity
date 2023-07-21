# Should create random individuals using both encodings

import unittest
import emr.controller
from emr.controller.custom_controller import CustomController
from emr.controller.phase_coupled_oscillator import PhaseCoupledOscillator
from emr.controller import decentralized_controller
from emr.encoding import robot_graph
from emr.encoding import graph_grammar
from emr.encoding.direct_encoding import DirectEncoding, configuration_handler
from emr.evolution import deap_interface as deap
from tqdm import tqdm

import emr.environment.evaluation as eval
import numpy as np

import random
from emr.config import config_handler

def custom_test(test_name : str, test_function, config = None, headless : bool = True) -> bool:
    print(f"---------------------------------")
    print(f"Testing {test_name} \n")
    try:
        if (config is not None):
            test_function(config, headless)
        else:
            test_function()
        print(f"---------------------------------")
        print(f"{test_name} : OK")
        print(f"---------------------------------")
        return True
    except:
        print(f"---------------------------------")
        print(f"{test_name} : Failed")
        print(f"---------------------------------")
        return False

def get_graph(encoding, controller, cfg):
    modules_to_use = configuration_handler.modules_to_use(cfg)
    enc_instance = encoding(controller, modules_to_use, cfg)
    return enc_instance.get_graph()

def innervate(encoding, controller, n_steps : int, n_random_individuals_to_test : int):
    print(f"-- Innervating: of {encoding.__name__} with {controller.__name__} ")
    config = configuration_handler.make_config()
    for _ in tqdm(range(n_random_individuals_to_test)):
        bp = get_graph(encoding, controller,config)
        ns = decentralized_controller.innervate_modules(bp)
        for i in range(n_steps):
            actions = np.ndarray(shape=(1,50),dtype=np.float32)
            sensory_input = np.ndarray(shape=(1,50),dtype=np.float32)           
            bp.step(sensory_input,actions, 0.1)
    return True


def _test_custom_controller():
    cr = CustomController()
    input_buffer = [1]
    output_buffer = [1]
    for _ in range(10):
        cr.step(input_buffer, output_buffer, 1.0)
def _test_phase_coupled_oscillator():
    pco = PhaseCoupledOscillator(1.0,1.0,1.0,1.0,1,1)
    input_buffer = [1]
    output_buffer = [1]
    for _ in range(10):
        pco.step(input_buffer, output_buffer, 1.0)

# create a few random individuals with random controllers that are innervated and simply 
# make sure that execution doesn't fail
def _test_innervation_lsystem_with_phase_coupled_oscillator():
    innervate(graph_grammar.GraphGrammar, PhaseCoupledOscillator,10,10)
    
def _test_innervation_lsystem_with_custom_controller():
    innervate(graph_grammar.GraphGrammar, CustomController,10,10)
    
def _test_innervation_direct_encoding_with_phase_coupled_oscillator():
    innervate(DirectEncoding, PhaseCoupledOscillator,10,10)
    
def _test_innervation_direct_encoding_with_custom_controller():
    innervate(DirectEncoding, CustomController,10,10)  

    
def _test_unity_sims_evaluation(cfg, headless : bool = True):
    cfg['environment']['simulator_to_use'] = 'sims'
    modules_to_use = configuration_handler.modules_to_use(cfg)

    path = cfg['experiment']['executable_path']
    print(f"opening: {path}")
    for i in range(10):
        individual = graph_grammar.GraphGrammar(PhaseCoupledOscillator, modules_to_use, cfg)
        eval.evaluate_individual(individual, path, n_steps = 10,scene_number_to_load = int(cfg['experiment']['scene_number']), editor_mode = False, no_graphics = headless)
    eval.close_env()


def _test_unity_modular_robot_evaluation(cfg, headless : bool = True):
    cfg['environment']['simulator_to_use'] = 'modular_robot'
    modules_to_use = configuration_handler.modules_to_use(cfg)

    path = cfg['experiment']['executable_path']
    print(f"opening: {path}")
    for i in range(10):
        individual = graph_grammar.GraphGrammar(PhaseCoupledOscillator, modules_to_use, cfg)
        eval.evaluate_individual(individual, path, n_steps = 10,scene_number_to_load = int(cfg['experiment']['scene_number']), editor_mode = False, no_graphics = headless)
    eval.close_env()

def _test_unity_paleobot_evaluation(cfg, headless : bool = True):
    cfg['environment']['simulator_to_use'] = 'paleobot'
    modules_to_use = configuration_handler.modules_to_use(cfg)
    path = cfg['experiment']['executable_path']
    print(f"opening: {path}")
    for i in range(10):
        individual = graph_grammar.GraphGrammar(PhaseCoupledOscillator,modules_to_use, cfg)
        eval.evaluate_individual(individual, path, n_steps = 10,scene_number_to_load = int(cfg['experiment']['scene_number']), editor_mode = False, no_graphics = headless)
    eval.close_env()

def _test_deap_single_thread(cfg, headless : bool):
    test_name = "Single threaded deap test"
    modules_to_use = configuration_handler.modules_to_use(cfg)
    cfg['visualization']['headless'] = str(int(headless))
    cfg["ea"]["batch_size"] = "4"   
    ea = deap.EvolutionaryAlgorithm(eval.evaluate_individual, cfg, 
		graph_grammar.GraphGrammar, PhaseCoupledOscillator, modules_to_use,n_cores = 1, 
		run_number = 0)
    ea.run(cfg,5)

def _test_deap_mutlithreaded(cfg, headless : bool):
    test_name = "Multithreaded deap test"
    modules_to_use = configuration_handler.modules_to_use(cfg)
    cfg['visualization']['headless'] = str(int(headless))
    cfg["ea"]["batch_size"] = "8"   
    ea = deap.EvolutionaryAlgorithm(eval.evaluate_individual, cfg, 
		graph_grammar.GraphGrammar, PhaseCoupledOscillator,modules_to_use, n_cores = 4, 
		run_number = 0)
    ea.run(cfg,5)


def _test_recording_and_playback(cfg, headless = True):
    np.random.seed(1)
    random.seed(4)


    n_tests = 4

    path = cfg['experiment']['executable_path']
    print(f"opening: {path}")
    modules_to_use = config_handler.modules_to_use(cfg)
    for i in range(n_tests):
        individual = graph_grammar.GraphGrammar(PhaseCoupledOscillator,modules_to_use, cfg)
        print(f"Evaluating random graphgrammar individual {i}")
        eval.evaluate_individual(individual, path, n_steps = 100,scene_number_to_load = int(cfg['experiment']['scene_number']), editor_mode = False, no_graphics = headless, record = True)
        # playback recording to double check
        import time
        eval.env.reset()
        json = eval.channel.json_recording_of_individual
        print(f"Evaluating playback of random graphgrammar individual {i}")
        eval.playback_recording_individual(individual, json,   path, n_steps = 10,scene_number_to_load = int(cfg['experiment']['scene_number']))
    eval.env.reset()
    eval.close_env()

def test_deap(config, headless = True) -> str:
    test_results = []
    test_results.append(custom_test("DEAP single threaded", _test_deap_single_thread, config, headless))
    test_results.append(custom_test("DEAP multi-threaded", _test_deap_mutlithreaded, config, headless))
    if test_results.__contains__(False):
        return "DEAP tests: FAILED"
    else:
        return "DEAP tests: SUCCESS"

def test_environments(config, headless = True) -> str:
    test_results = []
    test_results.append(custom_test("Paleobot", _test_unity_paleobot_evaluation, config, headless))
    test_results.append(custom_test("Sims-like robots", _test_unity_sims_evaluation, config, headless))
    test_results.append(custom_test("Modular Robots", _test_unity_modular_robot_evaluation, config, headless))
    if test_results.__contains__(False):
        return "Environment tests: FAILED"
    else:
        return "Environment tests: SUCCESS"

def test_controllers() -> str:
    test_results = []
    test_results.append(custom_test("Custom Controller",_test_custom_controller))
    test_results.append(custom_test("Phase Coupled Oscillator Controller",_test_phase_coupled_oscillator))
    if test_results.__contains__(False):
        return "Controller tests: FAILED"
    else:
        return "Controller tests: SUCCESS"

def test_innervation() -> str:
    test_results = []
    test_results.append(custom_test("direct encoding with phase coupled oscillator Controller",_test_innervation_direct_encoding_with_phase_coupled_oscillator))
    test_results.append(custom_test("direct encoding with custom controller",_test_innervation_direct_encoding_with_custom_controller))
    test_results.append(custom_test("graph grammar encoding with custom controller",_test_innervation_lsystem_with_phase_coupled_oscillator))
    test_results.append(custom_test("graph grammar with custom controller",_test_innervation_lsystem_with_custom_controller))
    if test_results.__contains__(False):
        return "Innervation tests: FAILED"
    else:
        return "Innervation tests: SUCCESS"


def test_recording_and_playback(cfg, headless = True) -> str:
    
    test_results = []
    test_results.append(custom_test("recording and playback",_test_recording_and_playback, cfg, headless))
    if test_results.__contains__(False):
        return "Recording and Playback tests: FAILED"
    else:
        return "Recording and Playback tests: SUCCESS"
   
def run_all_tests(config, headless = True):
    results = []
    results.append(test_controllers())
    results.append(test_innervation())
    results.append(test_environments(config, headless=headless))
    results.append(test_deap(config, headless=headless))
    results.append(test_recording_and_playback(config, headless=headless))
    
    print(f"\n")
    print("Test Results")
    for t in results:
        print(f" -- {t}")
