
from reprlib import recursive_repr
import uuid
import json
import random
import emr.config.config_handler as ch


# below should move
def forward_pass(robot_graph,controller_list):
	# set the inputs of all the innervated controllers
	for i,controller in enumerate(controller_list):
		#controller = controller_list[controller_key]
		for j,other_key in enumerate(controller.parents):
			nerve = controller.parents[other_key]
			robot_graph.innervation[other_key].forward_pass(nerve.index,nerve.value)
		for j,other_key in enumerate(controller.children):
			nerve = controller.children[other_key]
			robot_graph.innervation[other_key].forward_pass(nerve.index,nerve.value)
	pass

def step_update_controllers(controller_list, sensory_input, actions, delta_time):
	action_index = 0
	for i,controller in enumerate(controller_list):
		n_outputs = controller.controller.number_of_outputs
		target_actions = controller.step([sensory_input[0][i]], [actions[0][action_index]], delta_time)
		# temp debug: print( f"{n_outputs} and {action_index} and target actions size = {len(target_actions)}")
		for act in target_actions:
			actions[0][action_index] = act
			action_index+=1
	return actions
	pass

class Blueprint:
	""" 
	The blueprint represents a graph with defining how the modules should be connected. 
	The nodes are sent as JSON strings to Unity where they will be interpreted into robots. 
	The controllers are not sent to Unity but are used to set joints in the step method.
	"""
	def __init__(self):
		self.nodes = dict()
		self.controllers = dict()
		self.innervation = dict()
		#self.controller_list = []
	
	@staticmethod
	def random(n_nodes: int, controller_reference, module_options):
		"""
		return random blueprint (direct encoding)
		"""
		import emr.encoding.robot_module_utility as module_utility

		random_blueprint = Blueprint()
        # "EmergeModuleUnpacked" is the name of the module game object that is used in Unity. All the modules to be used from
        # the python side should be stored in a dictionary. This should probably also contain a variable with the number of connection sites. 
		random_module = random.choice(list(module_options))
		random_blueprint.nodes.update({"root":Node("root",type = random_module)})

		random_blueprint.controllers.update({"root":controller_reference.random('root')})
		for i in range(n_nodes):
			node_hash = str(uuid.uuid4())
			parent_node = random.choice(list(random_blueprint.nodes.keys()))
			node_type = random_blueprint.nodes[parent_node].type
			connection_site = str(random.randint(0,module_options[node_type].number_of_connection_sites-1))
			children_of_parent = random_blueprint.get_children(parent_node,random_blueprint.nodes)
			can_create_new_node = True
			for c in children_of_parent:
				if (random_blueprint.nodes[c].connection_site == connection_site):
					can_create_new_node = False
			if (can_create_new_node):
				module_type = random.choice(list(module_options))
				angle = module_utility.get_random_angle(module_type)
				random_blueprint.nodes.update({node_hash:Node(node_hash,parent=parent_node, connection_site =connection_site,type=module_type,angle=angle)})
				random_blueprint.controllers.update({node_hash:controller_reference.random(node_hash)})
		return random_blueprint
	

	def recursive_print(self,key, tree_string : str = "", depth = ""):
		children = []
		new_tree_string = f"{tree_string}{depth}{self.nodes[key].type} "
		new_tree_string = new_tree_string + f", Innervation = {len(self.innervation[key].parents)},{len(self.innervation[key].children)} type: {self.controllers[key].print()}\n"
		for n in self.nodes:
			if self.nodes[n].parent == key:
				children.append(n)
				new_tree_string = self.recursive_print(n, tree_string = new_tree_string, depth = depth + "-")
		return new_tree_string

	def print(self):
		print("Robot tree:")
		tree_string = self.recursive_print('root', depth = "|")
		print(tree_string)

	@staticmethod
	def get_children(key, dictionary):
		children = []
		for n in dictionary:
			if dictionary[n].parent == key:
				children.append(n)
		return children

	def has_children(self,key):
		for n in self.nodes.values():
			if (n.parent == key):
				return True
		return False

	def nodes_toJSON(self):
		json_nodes = []
		for n in self.nodes:
			json_nodes.append(self.nodes[n].to_dict())
		json_blueprint = JsonBlueprint(json_nodes)
		return json.dumps(json_blueprint.to_json())
	
	def add_module(self, parent_node : str = None, connection_site : int = 0, angle = [0,0,0], scale = [1,1,1]):
		node_hash = str(uuid.uuid4())
		self.nodes.update({node_hash:Node(node_hash, parent=parent_node, connection_site = connection_site, type = 'EmergeModuleUnpacked', angle=angle, scale = scale)})

	def step(self, sensory_input, actions, delta_time):
		controller_list = []
		for k in self.innervation:
			controller_list.append(self.innervation[k])
		forward_pass(self, controller_list)
		actions = step_update_controllers(controller_list, sensory_input, actions,delta_time)
		return actions

	def prune(self, keys_in_robot):
		# TODO, test pruning, not working yet
		# Prune graph to make it easier to work with? No computational bottleneck maybe?
		keys_not_in_robot = []
		if (len(keys_in_robot) > 0):
			print(f"Pruning {len(keys_in_robot)} nodes that were not expressed in the simulator")
		for n in self.nodes:
			if not keys_in_robot.__contains__(n):
				keys_not_in_robot.append(n)
		for k in keys_not_in_robot:
			self.controllers.pop(k)
			self.nodes.pop(k)
			self.innervation.pop(k)
		for n in self.innervation:
			for nerve in self.innervation[n].parents:
				if (keys_not_in_robot.__contains__(nerve)):
					self.innervation[n].parents.pop(nerve)
			for nerve in self.innervation[n].children:
				if keys_not_in_robot.__contains__(nerve):
					self.innervation[n].children.pop(nerve)
			for nerve in self.innervation[n].inputs:
				if keys_not_in_robot.__contains__(nerve):
					self.innervation[n].inputs.pop(nerve)

class JsonBlueprint():
	# Unity's JsonUtility doesn't like Dictionaries in json format so a list is used instead.
	# This class is responsible for creating the list
	def __init__(self, nodes):
		self.nodes = nodes
	def to_json(self):
		return self.__dict__


# Danger zone
## This object is interpreted by Unity as JSON. Any field name that is changed in here will need 
## to be changed in Unity as well. 

class Node():
	def __init__(self, name : str, parent : str = "a" , connection_site : str = "0", type : str = "c", angle = [0,0,0], scale = [1,1,1], rgb = [0.0,0.0,1.0]):
		self.name = name
		self.parent = parent
		self.connection_site = connection_site
		self.type = type
		self.euler_angles = angle
		self.scale = scale
		self.rgb = rgb
	def to_dict(self):
		return self.__dict__
