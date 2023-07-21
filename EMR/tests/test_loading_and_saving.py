# Should create random individuals using both encodings

import unittest
import emr.controller
from emr.controller.custom_controller import CustomController
from emr.controller.phase_coupled_oscillator import PhaseCoupledOscillator
from emr.controller import decentralized_controller
from emr.encoding import robot_graph
from emr.encoding import LSystem
from emr.encoding.direct_encoding import DirectEncoding
from emr.evolution import deap_interface as deap


import emr.environment.evaluation as eval
import numpy as np


from emr.config import config_handler
cfg = config_handler.make_config()


def get_graph(encoding, controller):
    enc_instance = DirectEncoding(controller, cfg)
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



class TestUnity(unittest.TestCase):
    def test_unity_record_playback(self):
        import random
        import numpy as np
        np.random.seed(1)
        random.seed(4)
        config_handler.SIMULATOR_TO_USE = config_handler.SimulatorToUse.ModularRobot3D
        cfg = config_handler.make_config()
        
        path = cfg['experiment']['executable_path']
        print(f"opening: {path}")
        success = False
        try:
            for i in range(10):
                individual = LSystem.GraphGrammar(PhaseCoupledOscillator, cfg)
                eval.evaluate_individual(individual, path, n_steps = 50,scene_number_to_load = int(cfg['experiment']['scene_number']), editor_mode = False, no_graphics = False, record = True)
                # playback recording to double check
                import time
                eval.env.reset()
                json = eval.channel.json_recording_of_individual
                eval.playback_recording_individual(individual, json,   path, n_steps = 50,scene_number_to_load = int(cfg['experiment']['scene_number']))
                eval.env.reset()
                json = eval.channel.json_recording_of_individual
                eval.playback_recording_individual(individual, json,   path, n_steps = 50,scene_number_to_load = int(cfg['experiment']['scene_number']))
            eval.env.reset()


        #eval.close_env()
            success = True
        except:
            print("Unable to open Unity environment")
            success = False
        self.assertEqual(success, True)


if __name__ == '__main__':
    print ("\n Running Tests: \n")
    unittest.main()



