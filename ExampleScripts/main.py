#import src.emr as emr

from emr import encoding, controller, environment, evolution, config
from tqdm import tqdm

if __name__ == "__main__":
    cfg =  config.config_handler.make_config()
    cfg['visualization']['headless'] = '0'
    cfg['environment']['evaluation_steps'] = '500'
    cfg['experiment']['executable_path'] = "D:\\Onedrive Personal\\OneDrive\\2_Projects\\Unity\\ModularRobots\\Build2023c\\EvolvingModularRobots"
    config.config_handler.print_config(cfg)
    encoding_reference, controller_reference, evaluation_function_reference = config.config_utility.get_encoding_controller_and_evaluation_from_config(cfg)
    config.config_handler.save_config("config.cfg", cfg)
    modules_to_use = config.config_handler.modules_to_use(cfg)
    ea = evolution.deap_interface.EvolutionaryAlgorithm(evaluation_function_reference, cfg, encoding_reference, controller_reference, modules_to_use, n_cores = 1)
    ea.initialize(cfg)
    
    for _ in tqdm(range(1), "Generation: "):
        ea.epoch()
    
    ea.close()