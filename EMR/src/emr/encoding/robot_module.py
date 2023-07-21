import random
import emr.encoding.robot_module_utility as util

class Module:
    def __init__(self, config, symbol_name : str, type : str = "EmergeModule", controller_reference = None, controller = None, parent : str = None, connection_site : str = None, angle = [0,0,0], scale = [1,1,1], number_of_connection_sites : int = 3, fix_controller : bool = False):
        self.symbol_name = symbol_name
        self.parent = parent
        self.connection_site = connection_site
        self.number_of_connection_sites = number_of_connection_sites
        self.angle = angle
        self.scale = scale
        self.controller = controller
        self.type = type
        if (controller_reference != None):
            self.controller = controller_reference.random(symbol_name, 
                number_of_inputs = int(config["control"]["number_of_inputs_per_module"]),
                number_of_outputs = int(config["control"]["number_of_outputs_per_module"]),
                )
            self.controller.fixed = fix_controller
    def mutate(self, mutation_rate, mutation_spread,controller_mutation_rate):
        # mutate angle of attachment
        if (random.uniform(0,1)< mutation_rate):
            self.angle = util.mutate_angle(self.symbol_name, self.angle, mutation_spread)
        # mutate controller
        if (self.controller is not None):
            self.controller.mutate(controller_mutation_rate, mutation_spread)

