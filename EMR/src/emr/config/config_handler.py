import configparser
import argparse

class ModuleInformation:
    def __init__(self, name : str, number_of_connection_sites : int, hasController : bool):
        self.name = name
        self.number_of_connection_sites = number_of_connection_sites
        self.hasController = hasController

def modules_to_use(config, emerge : bool = True):
    # Populates a dictionary based on the modules to use
	modulesToUseDictionary = dict()
	config['control']['number_of_outputs_per_module'] = '1'

	if config['environment']['simulator_to_use'] == "cube":
		modulesToUseDictionary.update({"CubePrefab":ModuleInformation("CubePrefab", 3, True)})
		config['experiment']['scene_number'] = '2'
	elif config['environment']['simulator_to_use'] ==  "paleobot":
		modulesToUseDictionary.update({"TriloSegment": ModuleInformation("TrilobyteSegment", 1, True)})
		config['experiment']['scene_number'] = '3'
		config['control']['number_of_outputs_per_module'] = '5'
	elif config['environment']['simulator_to_use'] == "modular_robot":
		if (emerge):
			modulesToUseDictionary.update({"EmergeModule":ModuleInformation("EmergeModule", 3, True)})
		else:
			modulesToUseDictionary.update({"GrammarBotStatic":ModuleInformation("GrammarBotStatic", 3, False)})
			modulesToUseDictionary.update({"GrammarBotJoint Variant":ModuleInformation("GrammarBotJoint Variant", 3, False)})
			modulesToUseDictionary.update({"GrammarBotJoint":ModuleInformation("GrammarBotJoint", 3, False)})
			modulesToUseDictionary.update({"TestModule":ModuleInformation("TestModule", 3, False)})
		config['experiment']['scene_number'] = '1'
	return modulesToUseDictionary

def make_config(experiment_nr:int = 0,
				mutation_probability: float =None,
				morphological_mutation_probability: float=None,
				mutation_spread:float =None,encoding =None, 
				controller_type = None, 
				experiment_path : str = "exp0/", duplicate_nr = 0, 
				replacement_type = None, 
				simulator_to_use = None):
	
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
	config['experiment']['executable_path'] = "./EMR_Executable/EvolvingModularRobots"	
	config['experiment']['scene_number'] = "1"

	# === Placedholder for environmental settings ===
	config['environment'] = {}
	config['environment']['terrain'] = '.'
	config['environment']['simulator_to_use'] = "modular_robot"
	config['environment']['modules_to_use'] = 'EmergeModule'
	config['environment']['evaluation_steps'] = '10'
	config['environment']['run_in_editor_mode'] = '0'

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
	config['ea']['n_cores'] = '1'
	
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
	config['evaluation'] = {}

	# === Encoding Settings ===
	config['encoding'] = {}
	if encoding is None:
		print("No encoding specified, using a direct encoding")
		encoding = 'graphgrammar'
	config['encoding']['type'] = encoding	
	
	# === Controller Settings ===
	config['control'] = {}
	if controller_type is None:
		controller_type = 'pco'
		print("No controller specified, using a ",controller_type," controller")
		
	config['control']['type'] = controller_type
	config['control']['donwstream_connection'] = '0'
	config['control']['number_of_inputs_per_module'] = '0'
	config['control']['number_of_outputs_per_module'] = '1'
	
	# override a few entries based on simulator to use
	if (simulator_to_use != None):
		if (simulator_to_use == 'cube'):
			config['environment']['modules_to_use'] = 'CubePrefab'
			config['experiment']['scene_number'] = "2"
		elif(simulator_to_use == "paleobot"):
			config['environment']['modules_to_use'] = 'TriloSegment'
			config['experiment']['scene_number'] = "3"		
			config['control']['number_of_outputs_per_module'] = '5'
	
	# === Visualization ===
	config['visualization'] = {}
	#config['visualization']['v_tree'] = '0'
	#config['visualization']['v_progression'] = '0'
	#config['visualization']['v_debug'] = '0'
	# Not relevant for Unity simulation
	#config['visualization']['render_interval'] = '2'
	config['visualization']['headless'] = '1'
	
	print("=== Done making a new configuration ===")

	return config

def save_config(path : str, config):
	with open(path, 'w') as configfile:
		config.write(configfile)

def load_config(path : str):
	print(f"Loading config at {path}")
	config = configparser.ConfigParser()
	config.sections()
	config.read(path)
	return config

def print_config(config):
	print("Configuration Parser File Contains: ")
	for section in config.sections():
		print(f"-- [{section}]")
		for (key, val) in config.items(section):
			print(f"---- {key} : {val}")


# for overriding config parameters
def get_arguments_from_parser():
	exp_path = "exp0/"
	run_number = "1"
	n_cores = "1"
	mutation_rate = None
	n_generations = 100
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
