import configparser
import argparse
from enum import Enum

class SimulatorToUse(Enum):
	ModularRobot3D = 0,
	SimsLikeRobot = 1, 
	PaleoBot = 2
	#ModularRobot2D = 3 # Under development

# This is an important variable to set. 
SIMULATOR_TO_USE = SimulatorToUse.ModularRobot3D
# The y rotations of the ModularRobot3D approach.
modular_robot_angle_options = [[0,0,0],[0,90,0],[0,180,0],[0,270,0]]

class ModuleInformation:
    def __init__(self, name : str, number_of_connection_sites : int, hasController : bool):
        self.name = name
        self.number_of_connection_sites = number_of_connection_sites
        self.hasController = hasController

def modules_to_use():
    # Populates a dictionary based on the modules to use
	modulesToUseDictionary = dict()
	if SIMULATOR_TO_USE == SimulatorToUse.SimsLikeRobot:
		modulesToUseDictionary.update({"SimsCube":ModuleInformation("SimsCube", 3, True)})
	# return mods
	# mods.append(ModuleInformation("CubeModule", 5, False))
    # mods.append(ModuleInformation("SimsModule", 5, False))
	elif SIMULATOR_TO_USE ==  SimulatorToUse.PaleoBot:
		modulesToUseDictionary.update({"TriloSegment": ModuleInformation("TrilobyteSegment", 1, True)})
	elif SIMULATOR_TO_USE == SimulatorToUse.ModularRobot3D:
		emerge = True
		if (emerge):
			modulesToUseDictionary.update({"EmergeModule":ModuleInformation("EmergeModule", 3, True)})
			#modulesToUseDictionary.update({"EmergeModuleSpring":ModuleInformation("EmergeModuleSpring", 3, True)})
			#modulesToUseDictionary.update({"LinearSpring":ModuleInformation("LinearSpring", 3, True)})
		else:
			modulesToUseDictionary.update({"GrammarBotStatic":ModuleInformation("GrammarBotStatic", 3, False)})
			modulesToUseDictionary.update({"GrammarBotJoint Variant":ModuleInformation("GrammarBotJoint Variant", 3, False)})
			modulesToUseDictionary.update({"GrammarBotJoint":ModuleInformation("GrammarBotJoint", 3, False)})
			modulesToUseDictionary.update({"TestModule":ModuleInformation("TestModule", 3, False)})
	#mods.append(ModuleInformation("LinearSpring", 3, False))
	return modulesToUseDictionary

MIN_ANGLE = -45
MAX_ANGLE = 45

# Below should be moved to another script
import random
def get_random_angle():
	if (SIMULATOR_TO_USE == SimulatorToUse.ModularRobot3D):
		return random.choice(modular_robot_angle_options)
	else:
		#return [0,0,0]
		return [random.uniform(MIN_ANGLE,MAX_ANGLE),random.uniform(MIN_ANGLE,MAX_ANGLE),random.uniform(MIN_ANGLE,MAX_ANGLE)]

def mutate_angle(angle, sigma):
	if (SIMULATOR_TO_USE == SimulatorToUse.ModularRobot3D):
		return random.choice(modular_robot_angle_options)
	else:
		#return angle
		for i in range(len(angle)):
			angle[i] = max(min(random.gauss(angle[i],sigma), MAX_ANGLE), MIN_ANGLE)
		return angle


def make_config(experiment_nr:int = 0,mutation_probability: float =None,morphological_mutation_probability: float=None,mutation_spread:float =None,enc =None, controller_type = None, experiment_path : str = "exp0/", duplicate_nr = 0, replacement_type = None):
	
	print("=== Making a new config ===")
	config = configparser.ConfigParser()

	# === Experiment Settings ===
	config['experiment'] = {}
	config['experiment']['checkpoint_frequency'] = '50'
	config['experiment']['save_elite'] = '1'
	# where to store the data
	config['experiment']['experiment_path'] = experiment_path
	config['experiment']['save_files_prefix'] = ''
	config['experiment']['seed'] = str(duplicate_nr)
	config['experiment']['executable_path'] = "D:\\Onedrive Personal\\OneDrive\\2_Projects\\Unity\\ModularRobots\\Build2023b"
	
	if SIMULATOR_TO_USE == SimulatorToUse.ModularRobot3D:
		config['experiment']['scene_number'] = "1"
	elif SIMULATOR_TO_USE == SimulatorToUse.SimsLikeRobot: 
		config['experiment']['scene_number'] = "2"
	elif SIMULATOR_TO_USE == SimulatorToUse.PaleoBot:
		config['experiment']['scene_number'] = "3"

	# === Placedholder for environmental settings ===
	config['environment'] = {}
	config['environment']['terrain'] = '.'

	# === Settings of the evolutionary algorithm ===
	config['ea'] = {}
	# total number of evaluations: note that generations is calculated as 'n_evaluations' / 'batch_size'
	config['ea']['n_evaluations'] = '25600'
	# Number of individuals evaluated per generation 
	config['ea']['batch_size'] = '24'
	# Number of elites that will not be mutated
	config['ea']['elitism'] = '1'
	# probability for controller mutations
	if mutation_probability is None:
		print('No mutation rate specified, using 0.1 as default')
		mutation_probability = 0.1
	config['ea']['mutation_prob'] = str(mutation_probability)
	# probability for morphology mutations
	if morphological_mutation_probability is None:
		print('No <<morphology>> mutation rate specified, using 0.1 as default')
		morphological_mutation_probability = 0.1
	config['ea']['morphmutation_prob'] = str(morphological_mutation_probability)
	# sigma value for both types of mutations
	if mutation_spread is None:
		print('No mutation sigma value specified, using 0.1 as default')
		mutation_spread = 0.1

	config['ea']['mutation_sigma'] = str(mutation_spread)
	# showing the best individual after each run (note, box2D time-out can lead to frozen window)
	config['ea']['show_best'] = '0'
	# In case you simply want to load the best individuals
	config['ea']['load_best'] = '0'
	# number of dedicated CPU cores for the experiments
	config['ea']['n_cores'] = '6'
	
	# placeholders, not implemented in this version
	# config['ea']['crossover_prob']
	config['ea']['interval'] = '50'
	config['ea']['max_evaluation_steps'] = '5000000'
	config['ea']['wallclock_time_limit'] = '50000000';
	
	# selection operators
	# offspring selection, options: 
	config['ea']['selection'] = 'tournament'; 
	config['ea']['selection_meta'] = '3'; # e.g. tournament size 
	# survivor selection, options:
	config['ea']['replacement'] = 'tournament'; 
	config['ea']['replacement_meta'] = '3'; 
	if (replacement_type is not None):
		config['ea']['replacement'] = replacement_type

	config['morphology'] = {}
	# A robot can be composed of up to 'max_size' modules
	config['morphology']['max_size'] = '40'
	# The maximum depth of the tree blueprint
	config['morphology']['max_depth'] = '7'
	# config['morphology']['m_rectangle'] = '4'
	# config['morphology']['m_circular'] = '4'
	# config['morphology']['usable_modules'] = 'simple2d,circle2d,simple2d,circle2d,simple2d,circle2d'
	# config['morphology']['usable_modules'] = 'simple2d,circle2d'

	config['evaluation'] = {}
	# The speed at which the wall of death moves forward
	# TODO
	#config['evaluation']['wod_speed'] = '0.5'

	# === Encoding Settings ===
	config['encoding'] = {}
	if enc is None:
		print("No encoding specified, using a direct encoding")
		enc = 'lsystem'
	config['encoding']['type'] = enc	
	
	# === Controller Settings ===
	config['control'] = {}
	if controller_type is None:
		controller_type = 'cpgn'
		print("No controller specified, using a ",controller_type," controller")
		
	config['control']['type'] = controller_type
	config['control']['donwstream_connection'] = '0'
	config['control']['number_of_inputs_per_module'] = '0'
	config['control']['number_of_outputs_per_module'] = '1'
	if (SIMULATOR_TO_USE == SimulatorToUse.PaleoBot):
		config['control']['number_of_outputs_per_module'] = '4'
			
	
	# === Visualization ===
	config['visualization'] = {}
	config['visualization']['v_tree'] = '0'
	config['visualization']['v_progression'] = '0'
	config['visualization']['v_debug'] = '0'
	# Not relevant for Unity simulation
	config['visualization']['render_interval'] = '2'
	config['visualization']['headless'] = '1'
	
	print("=== Done making a new configuration ===")

	return config

# for overriding config parameters
def get_arguments_from_parser():
	exp_path = "exp0/"
	run_number = "1"
	n_cores = "1"
	mutation_rate = None
	n_generations = 100
	port_id = 0
	parser = argparse.ArgumentParser()
	parser.add_argument("--exp_path")
	parser.add_argument("--run_number")
	parser.add_argument("--n_cores")
	parser.add_argument("--mutation_rate")
	parser.add_argument("--n_generations")
	args, leftovers = parser.parse_known_args()

	if args.exp_path is not None:
		exp_path = args.exp_path
		exp_path = exp_path + "/"
		print("exp_path has been set (value is %s)" % args.exp_path)
	else:
		print(f"Starting evolutionary run without arguments. Experiment name set to '{exp_path}'")
	if args.run_number is not None:
		run_number = int(args.run_number)
		print("run_number has been set (value is %s)" % args.run_number)
	if args.n_cores is not None:
		n_cores = int(args.n_cores)
		print("n_cores has been set (value is %s)" % args.n_cores)
	if args.mutation_rate is not None:
		mutation_rate = float(args.mutation_rate)
		print(f"mutation_rate has been set to {mutation_rate}")
	if args.n_generations is not None:
		n_generations = int(args.n_generations)
		print(f"n_generations has been set to {n_generations}")
	return exp_path, run_number, n_cores, mutation_rate, n_generations
