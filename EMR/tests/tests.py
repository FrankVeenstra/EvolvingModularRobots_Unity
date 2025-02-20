# Should create random individuals using both encodings

import unittest
import emr.controller
from emr.controller.custom_controller import CustomController
from emr.controller.phase_coupled_oscillator import PhaseCoupledOscillator
from emr.controller import decentralized_controller
from emr.encoding import robot_graph
from emr.encoding import graph_grammar
from emr.encoding.direct_encoding import DirectEncoding
from emr.evolution import deap_interface as deap


import emr.environment.evaluation as eval
import numpy as np


from emr.config import config_handler
cfg = config_handler.make_config()

def get_graph(encoding, controller):
    modules_to_use = config_handler.modules_to_use(cfg)
    enc_instance = DirectEncoding(controller, modules_to_use, cfg)
    return enc_instance.get_graph()

def innervate(encoding, controller, n_steps : int, n_random_individuals_to_test : int):
    print(f"\nTesting innervation of {encoding.__name__} with {controller.__name__} ")

    try:
        for _ in range(n_random_individuals_to_test):
            bp = get_graph(encoding, controller)
            ns = decentralized_controller.innervate_modules(bp)
            for i in range(n_steps):
                actions = np.ndarray(shape=(1,50),dtype=np.float32)
                sensory_input = np.ndarray(shape=(1,50),dtype=np.float32)           
                bp.step(sensory_input,actions, 0.1)
        return True
    except: 
        return False

class TestController(unittest.TestCase):
    def test_custom_controller(self):
        print(f"Testing {CustomController.__name__}\n")
        cr = CustomController()
        input_buffer = [1]
        output_buffer = [1]
        self.assertGreater(len(cr.step(input_buffer, output_buffer, 0.1)),0)
    def test_phase_coupled_oscillator(self):
        print(f"Testing {PhaseCoupledOscillator.__name__}\n")
        pco = PhaseCoupledOscillator(1.0,1.0,1.0,1.0,1,1)
        input_buffer = [1]
        output_buffer = [1]
        self.assertGreater(len(pco.step(input_buffer, output_buffer, 0.1)),0)

class TestInnervation(unittest.TestCase):
    # create a few random individuals with random controllers that are innervated 
    def test_innervation_lsystem_with_phase_coupled_oscillator(self):
        self.assertEqual(innervate(graph_grammar.GraphGrammar, PhaseCoupledOscillator,10,10), True)
    
    def test_innervation_lsystem_with_custom_controller(self):
        self.assertEqual(innervate(graph_grammar.GraphGrammar, CustomController,10,10), True)
    
    def test_innervation_direct_encoding_with_phase_coupled_oscillator(self):
        self.assertEqual(innervate(DirectEncoding, PhaseCoupledOscillator,10,10), True)
    
    def test_innervation_direct_encoding_with_custom_controller(self):
        innervate(DirectEncoding, CustomController,10,10)
        self.assertEqual(innervate(DirectEncoding, CustomController,10,10), True)    

class TestUnity(unittest.TestCase):
    def test_unity_sims_evaluation(self):
        cfg = config_handler.make_config()
        path = cfg['experiment']['executable_path']
        modules_to_use=config_handler.modules_to_use(cfg)
        print(f"opening: {path}")
        success = False
        try:
            for i in range(10):
                individual = graph_grammar.GraphGrammar(PhaseCoupledOscillator, modules_to_use, cfg)
                eval.evaluate_individual(individual, path, n_steps = 10,scene_number_to_load = int(cfg['experiment']['scene_number']), editor_mode = False, no_graphics = False)
            eval.close_env()
            success = True
        except:
            print("Unable to open Unity environment")
            success = False
        self.assertEqual(success, True)

    def test_unity_modular_robot_evaluation(self):
        cfg = config_handler.make_config()
        modules_to_use = config_handler.modules_to_use(cfg)
        path = cfg['experiment']['executable_path']
        print(f"opening: {path}")
        success = False
        try:
            for i in range(10):
                individual = graph_grammar.GraphGrammar(PhaseCoupledOscillator, modules_to_use,cfg)
                eval.evaluate_individual(individual, path, n_steps = 10,scene_number_to_load = int(cfg['experiment']['scene_number']), editor_mode = False, no_graphics = False)
            eval.close_env()
            success = True
        except:
            print("Unable to open Unity environment")
            success = False
        self.assertEqual(success, True)


    def test_unity_paleobot_evaluation(self):
        cfg = config_handler.make_config()
        path = cfg['experiment']['executable_path']
        modules_to_use = config_handler.modules_to_use(cfg)

        print(f"opening: {path}")
        success = False
        try:
            for i in range(10):
                individual = graph_grammar.GraphGrammar(PhaseCoupledOscillator, modules_to_use, cfg)
                eval.evaluate_individual(individual, path, n_steps = 10,scene_number_to_load = int(cfg['experiment']['scene_number']), editor_mode = False, no_graphics = False)
            eval.close_env()
            success = True
        except:
            print("Unable to open Unity environment")
            success = False
        self.assertEqual(success, True)


    def test_deap_mutlithreaded(self):
        success = False
        modules_to_use = config_handler.modules_to_use(cfg)
        try:
            cfg["ea"]["batch_size"] = "8"   
            ea = deap.EvolutionaryAlgorithm(eval.evaluate_individual, cfg, 
		        graph_grammar.GraphGrammar, PhaseCoupledOscillator, modules_to_use, n_cores = 4, 
		        run_number = 0, number_of_evaluation_steps = 10)
            ea.run(cfg,5)
            success = True
            print("Multithreaded test was OK")
        except:
            success = False
        self.assertEqual(success, True)

if __name__ == '__main__':
    print ("\n --- Running Tests: --- \n")   
    unittest.main()

