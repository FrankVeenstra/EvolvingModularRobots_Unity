#import src.emr as emr

from emr import encoding, controller, environment, evolution, config
from tqdm import tqdm
import os 


def main():
    if not os.path.exists("EMR_Executable"):
        print("Cannot find executable directory")
        return
    cfg =  config.config_handler.make_config()
    cfg['visualization']['headless'] = '1'
    cfg['environment']['evaluation_steps'] = '500'
    cfg['experiment']['executable_path'] = "EMR_Executable/EvolvingModularRobots"
    cfg['environment']['simulator_to_use'] = 'modular_robot' 
    config.config_handler.print_config(cfg)
    encoding_reference, controller_reference, evaluation_function_reference = config.config_utility.get_encoding_controller_and_evaluation_from_config(cfg)
    modules_to_use = config.config_handler.modules_to_use(cfg)
    ea = evolution.deap_interface.EvolutionaryAlgorithm(evaluation_function_reference, cfg, encoding_reference, controller_reference, modules_to_use, n_cores = 4)
    ea.initialize(cfg)
    config.config_handler.save_config(cfg['experiment']['experiment_path'] + "config.cfg", cfg)
    
    for _ in tqdm(range(10), "Generation: "):
        ea.epoch()
    
    ea.close()
if __name__ == "__main__":
    main()