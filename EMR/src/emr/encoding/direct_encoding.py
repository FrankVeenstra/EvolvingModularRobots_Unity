#!/usr/bin/env python
from multiprocessing import connection
import numpy as np
import random

import emr.encoding.robot_graph as robot_graph
import copy
import uuid
import pickle 

import emr.encoding.robot_module
from emr.config import config_handler as configuration_handler
import emr.encoding.robot_module_utility as module_utility

max_number_of_add_module_mutations = 4

class DirectEncoding:
    def __init__(self, controller_reference, modules_to_use, config, fitness = -1.0, debug : bool = False):
        self.module_options = modules_to_use # modules to pick from       
        self.fitness = fitness
       
        # Flag indicating reevaluation is needed
        self.isDirty = True
        self.debug = debug
        self.controller_reference = controller_reference
        initial_number_of_modules = 5
        self.genome = robot_graph.Blueprint.random(initial_number_of_modules,controller_reference,self.module_options)
        self.mutate(0.5,0.5,0.5)
    def get_graph(self):
        return self.genome

    @staticmethod
    def random(controller_reference, config, fitness = -1.0, debug : bool = False):
        ind = DirectEncoding(controller_reference, config, fitness, debug)

    def mutate(self, morphology_mutation_rate, mutation_sigma, controller_mutation_rate):
        for i in range(max_number_of_add_module_mutations):
            if (random.uniform(0,1) < morphology_mutation_rate):
                self.add_random_module(debug=self.debug)
        if (random.uniform(0,1)< morphology_mutation_rate):
            self.remove_random_module(debug=self.debug)
        for c in self.genome.controllers:
            self.genome.controllers[c].mutate(controller_mutation_rate, mutation_sigma)
        for module in self.genome.nodes:           
            if (random.uniform(0,1) < morphology_mutation_rate):
                module_type = self.genome.nodes[module].type
                self.genome.nodes[module].euler_angles = module_utility.mutate_angle(module_type,self.genome.nodes[module].euler_angles,mutation_sigma)
        # TODO ==============================
        # 
        # ===================================
        # swap one node in dictionary 
        # ===================================
    def remove_random_module(self, debug : bool = False):
        # get random node
        if debug:
            print("Removing modules")
        root_node = random.choice(list(self.genome.nodes.keys()))
        if root_node == 'root':
            # cannot remove the root node
            return
        # remove all child nodes connected to the parent
        nodes_to_remove = [root_node]
        node_queue = [root_node]
        while len(node_queue) > 0:
            parent_node = node_queue.pop(0)
            for n in self.genome.nodes:
                node = self.genome.nodes[n]
                if (node.parent == parent_node):
                    node_queue.append(n)
                    nodes_to_remove.append(n)
        if debug:
            print(f"Should remove {len(nodes_to_remove)} nodes")
        for n in nodes_to_remove:
            del self.genome.nodes[n]
            del self.genome.controllers[n]
    
#    def recreate_controller_list(self):
#        self.genome.controller_list = []
#        for n in self.genome.controllers:
#            self.genome.controller_list.append(self.genome.controllers[n])


    def add_random_module(self, debug : bool = False):
        if debug:
            print(f"Should add node")
        node_hash = str(uuid.uuid4())
        parent_node = random.choice(list(self.genome.nodes.keys()))
        parent_node_type = self.genome.nodes[parent_node].type
        max_connections = self.module_options[parent_node_type].number_of_connection_sites
        connection_site = str(random.randint(0,max_connections-1))
        # pick a random connection site
        children_of_parent = self.genome.get_children(parent_node,self.genome.nodes)
        can_create_new_node = True
        # ensure a new module can be added to a connection site
        for c in children_of_parent:
            if (self.genome.nodes[c].connection_site == connection_site):
                can_create_new_node = False
        # create the new node in the genome/graph
        if (can_create_new_node):
            module_type = random.choice(list(self.module_options.keys()))
            angle = module_utility.get_random_angle(module_type)
            self.genome.nodes.update({node_hash:robot_graph.Node(node_hash,parent=parent_node, connection_site =connection_site, type = module_type,angle=angle)})
            self.genome.controllers.update({node_hash:self.controller_reference.random(node_hash)})
            # Above could copy parent properties
        
    @staticmethod
    def save(ind, path :str, filename : str):
        # save the symbol and rule dictionary
        with open(f'{filename}.pcl', 'wb') as fp:
            pickle.dump(ind, fp)
    @staticmethod
    def load(path : str, filename : str):
        # load the symbol and rule dictionary
        with open(f'{filename}','rb') as fp:
            return pickle.load(fp)