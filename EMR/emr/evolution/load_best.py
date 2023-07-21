from encoding import LSystem
from controller import custom_controller
import evaluation as ev

PATH = "TestRuns/run_0.04/exp"

def load_best(config, ea = None):
    from ea import deap_interface
    if (ea == None):
        for i in range(20):
            config['experiment']['experiment_path'] = f"{PATH}{i}"
            ea = deap_interface.EvolutionaryAlgorithm(ev.get_env, ev.evaluate_individual, config,
            LSystem.GraphGrammar, custom_controller.Controller, n_cores = 1, run_number = 0)
            ea.load_best()

if __name__ == "__main__":
    from configuration import config_handler
    config = config_handler.make_config()
    config['experiment']['experiment_path'] = PATH
    load_best(config)