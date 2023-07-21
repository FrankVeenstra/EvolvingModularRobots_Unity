#!/usr/bin/env python

from multiprocessing import connection

import numpy as np
import random

import emr.encoding.robot_graph as robot_graph
import emr.encoding.robot_module as rm
import emr.encoding.robot_module_utility as module_utility

import copy
import uuid
import pickle       


#class LNode:
#    def __init__(self, symbol) -> None:
#        self.n = robot_graph.Node(symbol, parent=None, connection_site= None, type = 'EmergeModuleUnpacked', angle=random.choice(robot_graph.angle_options))
#        pass


def get_number_of_children(s : str, module_dictionary):
    if (module_dictionary.__contains__(s)):
        return module_dictionary[s].number_of_connection_sites

class Symbol:
    def __init__(self, name : str):
        self.name = name
        self.representation = rm.Module()

# rule
# adding a mutable rewrite rule for every symbol
class Rule:
    def __init__(self, symbol : str):
        self.symbol = symbol
        #"Whenever the algorithm iterates through the 'symbol', it returns the product"
        self.product = dict() # int, symbol


    def random_rule(symbol :str, symbol_dictionary):
        rule = Rule(symbol)
        for i in range(get_number_of_children(symbol, symbol_dictionary)):
            # 50% chance to add a rule associated with the maximum number of children (leaf nodes) allowed
            if (random.uniform(0.0,1.0) < 0.5):
                # Connection site {i} will have symbol {random.choice(options)} associated with it
                rule.product.update({i:random.choice(list(symbol_dictionary.keys()))})
        return rule

    def iterate(self):
        """ returns a dictionary """
        return self.product

    @staticmethod
    def get_available_connection(product, max_number_of_children):
        children = []
        for k in product:
            children.append(int(k))
        connection_site = random.randint(0,max_number_of_children-1)
        while (children.__contains__(connection_site)):
            connection_site = random.randint(0,max_number_of_children-1)
        return str(connection_site)

    def mutate_number_of_children(self, symbol_dictionary, mutation_rate):
        max_number_of_children = get_number_of_children(self.symbol, symbol_dictionary)
        number_of_children = len(self.product)
        new_number_of_children = number_of_children
        if (random.uniform(0.0,1.0) < mutation_rate):
            new_number_of_children = random.randint(0,max_number_of_children-1)
        if (new_number_of_children != number_of_children):
            while (new_number_of_children < number_of_children):
                random_module_key = random.choice(list(self.product))
                self.product.pop(random_module_key)
                number_of_children-=1
            while (new_number_of_children > number_of_children):
                con = Rule.get_available_connection(self.product,max_number_of_children)
                self.product.update({con:random.choice(list(symbol_dictionary.keys()))})
                number_of_children+=1

    def mutate_symbols(self, symbol_dictionary, mutation_rate):
        for k in self.product:
            if (random.uniform(0,1) < mutation_rate):
                new_s = random.choice(list(symbol_dictionary.keys()))
                self.product[k] = new_s
        
    
    def mutate(self, symbol_dictionary, mutation_rate : float , mutation_spread : float):
        # change number of product
        self.mutate_number_of_children(symbol_dictionary, mutation_rate)
        # change symbol
        self.mutate_symbols(symbol_dictionary, mutation_rate)


class GraphGrammar:
    def __init__(self, controller_reference, modules_to_use, config, number_of_symbols : int = 5, fitness = -1.0) -> None:
        self.module_options = modules_to_use
        self.fitness = fitness
        # Flag indicating reevaluation is needed
        self.isDirty = True
        # symbol : module (how symbols map to modules)
        self.symbol_dictionary = dict()
        # symbol : rule (how symbols map to extension rules)
        self.rule_dictionary = dict() 
        self.random_rules(controller_reference, config, number_of_symbols = number_of_symbols)
        # For debugging; below should make identical robots every time
        #self.manual_rules(controller_reference, config, number_of_symbols = number_of_symbols)
    
    def random_rules(self, controller_reference, config, number_of_symbols = 5) -> None:        
        module_list = list(self.module_options)
        if (self.module_options is None):
            print("error: please pass on 'modules_to_use : dict' options")
        
        number_of_module_types_to_use = len(module_list)

        # stores the string references (for random.choice(options))
        self.options = []
        self.axiom = module_list[0]
        for i in range(number_of_symbols):
            moduleNr = i % number_of_module_types_to_use
            t = module_list[moduleNr]
            module = self.module_options[t]

            symbol_name = str(i)
            self.options.append(symbol_name)
            #fix = False # temp
            #if (module.name == "EmergeModuleSpring"):
            #    fix = True
            robot_module = rm.Module(config, symbol_name, 
                controller_reference = controller_reference, parent = 'none', connection_site='none', 
                angle = module_utility.get_random_angle(symbol_name),
                type = module.name, 
                number_of_connection_sites= module.number_of_connection_sites)
            self.symbol_dictionary.update({symbol_name: robot_module})
        for symbol_name in self.symbol_dictionary:
            self.rule_dictionary.update({symbol_name:Rule.random_rule(symbol_name,self.symbol_dictionary)})
        self.reset()
        
    def manual_rules(self, controller_reference, config, number_of_symbols : int = 5) -> None:
        if (self.module_options is None):
            print("error: please pass on module options")

        number_of_module_types_to_use = len(self.module_options)

        # stores the string references (for random.choice(options))
        self.options = []
        self.axiom =self. module_options[0].name
        for i in range(number_of_symbols):
            moduleNr = i % number_of_module_types_to_use
            module = self.module_options[moduleNr]
            t = module.name

            symbol_name = str(i)
            self.options.append(symbol_name)
            self.symbol_dictionary.update({symbol_name: rm.Module(symbol_name, 
                controller_reference = controller_reference, parent = 'none', connection_site='none', 
                angle = 90,type = module.name, 
                number_of_connection_sites= module.number_of_connection_sites,fix_controller=fix)})
        # create rules manually
        for i,symbol_name in enumerate(self.symbol_dictionary):
            if (i == 0):
                rule1 = Rule(self.symbol_dictionary["0"])
                rule1.product.update({1:"1"})
                rule1.product.update({2:"1"})
                rule1.product.update({3:"7"})
                rule1.product.update({4:"7"})
                self.rule_dictionary.update({symbol_name:rule1})
            elif (i == 1):
                rule2 = Rule(self.symbol_dictionary["0"])
                rule2.product.update({2:"4"})
                self.rule_dictionary.update({symbol_name:rule2})
            elif (i == 4):
                 rule3 = Rule(self.symbol_dictionary["0"])
                 rule3.product.update({2:"2"})
                 self.rule_dictionary.update({symbol_name:rule3})
            elif (i == 7):
                 rule4 = Rule(self.symbol_dictionary["0"])
                 rule4.product.update({2:"4"})
                 self.rule_dictionary.update({symbol_name:rule4})
            else:
                emptyRule = Rule(symbol_name)
                self.rule_dictionary.update({symbol_name:emptyRule})
        self.reset()

    def reset(self):
        root_name = 'root'
        # the tree in GraphGrammar form
        self.grammar_tree = dict()
        # add an axiom (root module) to the tree
        root_symbol = self.symbol_dictionary['0']

        self.grammar_tree.update({root_name:copy.deepcopy(root_symbol)})
                                                        #rm.Module(config,'0',
        #controller=root_symbol.controller,parent = 'none', connection_site='none',angle = [0,0,root_symbol.angle],type=self.axiom)})
        self.nodes_to_process_queue = []
        self.nodes_to_process_queue.append(list(self.grammar_tree.keys())[0])

    def mutate(self, mutation_rate : float, mutation_spread : float, controller_mutation_rate : float):
        for symbol_name in self.symbol_dictionary:
            symbol = self.symbol_dictionary[symbol_name]
            # controllers of symbols are also mutated
            symbol.mutate(mutation_rate, mutation_spread,controller_mutation_rate)
        for rule_name in self.rule_dictionary:
            rule = self.rule_dictionary[rule_name]
            rule.mutate(self.symbol_dictionary, mutation_rate, mutation_spread)
    

    def process_node(self, node_to_process):
        if node_to_process in self.rule_dictionary:
            return self.rule_dictionary[node_to_process].iterate()
        else:
            print(f"node_to_process was not in rule dictionary")

    def iterate(self, max_nodes : int = 50):
        """ expand the tree by looking at all the existing modules in 
        the tree and expanding their connections based on the rules """
        new_nodes_to_process = []
        while (len(self.nodes_to_process_queue) > 0):
            node_to_process = self.nodes_to_process_queue.pop()
            new_nodes = self.process_node(self.grammar_tree[node_to_process].symbol_name)
            for np in new_nodes:
                # np represents connection site
                if (len(self.grammar_tree) >= max_nodes-1):
                    return
                # add the new nodes to the tree
                # (1) create unique hash
                node_hash = str(uuid.uuid4())
                # (2) update the grammar tree referencing the parent
                symbol = self.symbol_dictionary[new_nodes[np]]
                fix = False
                if (symbol.controller):
                    fix = symbol.controller.fixed
                
                self.grammar_tree.update({node_hash:rm.Module(symbol,new_nodes[np],controller = symbol.controller,
                parent = node_to_process,connection_site = np,angle=symbol.angle,type = symbol.type, fix_controller=fix)})
                # (3) add new nodes to the existing queue to process the new nodes
                new_nodes_to_process.append(node_hash)
        for node in new_nodes_to_process:
            self.nodes_to_process_queue.append(node)
    
    @staticmethod
    def grammar_tree_to_graph_tree(tree, colors = None):
        if colors is None:
            import matplotlib.cm as cm
            number_of_rules = len(tree.symbol_dictionary)
            colors = []
            for i in range(number_of_rules):
                colors.append(cm.viridis(float(i)/(number_of_rules)))

        bp = robot_graph.Blueprint()
        for n in tree.grammar_tree:
            node = copy.deepcopy(tree.grammar_tree[n])
            color = colors[int(node.symbol_name)]
            # TODO change the module types to a dictionary/enum or something referenced somewhere
            bp.nodes.update({n:robot_graph.Node(n, parent=node.parent, 
            connection_site = node.connection_site, 
            type = node.type,angle=node.angle, rgb=[color[0],color[1],color[2]])})
            bp.controllers.update({n:copy.deepcopy(node.controller)})
        return bp
        
    def get_graph(self, number_of_iterations = 8):
        self.reset()
        for i in range(number_of_iterations):
            self.iterate()
        return GraphGrammar.grammar_tree_to_graph_tree(self)
            
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


def get_random_l_tree(Controller):
    default_number_of_rules = 12
    from configuration import config_handler as ch
 
    import matplotlib.cm as cm
    colors = []
    for i in range(default_number_of_rules):
        colors.append(cm.viridis(float(i)/default_number_of_rules))
    l = GraphGrammar(Controller,default_number_of_rules, ch.modules_to_use())
    for i in range(8):
        l.iterate()
    return GraphGrammar.grammar_tree_to_graph_tree(l, colors)


def save_test(Controller):
    import matplotlib.cm as cm
    from configuration import config_handler as ch
    default_number_of_rules = 8
    colors = []
    for i in range(default_number_of_rules):
        colors.append(cm.viridis(float(i)/default_number_of_rules))
    l = GraphGrammar(Controller,None, default_number_of_rules, ch.modules_to_use())
    for i in range(4):
        l.iterate()
    GraphGrammar.save(l,"","")
    r = GraphGrammar.load("","")
    pass

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from controller import custom_controller
    for i in range(1):
        g = save_test(custom_controller.Controller)


