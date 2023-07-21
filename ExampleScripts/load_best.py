from emr import encoding, controller, environment, evolution, config


if __name__ == "__main__":
    
    cfg = config.config_handler.load_config("config.cfg") 
    config.config_handler.print_config(cfg)
    encoding_reference, controller_reference, evaluation_function_reference = config.config_utility.get_encoding_controller_and_evaluation_from_config(cfg)

    # Fetching the modules that can be used 
    modules_to_use = config.config_handler.modules_to_use(cfg)

    # creating a standard evolutionary algorithm that using `deap` 
    ea = evolution.deap_interface.EvolutionaryAlgorithm(evaluation_function_reference, cfg, encoding_reference, controller_reference, modules_to_use)
    ea.load_best(cfg)
    ea.close()