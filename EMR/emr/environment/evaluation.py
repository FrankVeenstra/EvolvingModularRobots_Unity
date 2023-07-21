import multiprocessing
from re import L
from mlagents_envs.environment import UnityEnvironment

from mlagents_envs.base_env import (
    ActionTuple
    )
from emr.unity.unity_side_channel import CustomSideChannel
from sys import platform
import numpy as np
import random
from emr.controller import decentralized_controller


GLOBAL_SOCKET_OFFSET = 400
#RUN_IN_EDITOR_MODE = False
#NO_GRAPHICS = False

# singleton equivalent
env = None
channel = None

import socket
HIGHEST_WORKER_ID = 65535 - UnityEnvironment.BASE_ENVIRONMENT_PORT
def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def is_worker_id_open(worker_id: int) -> bool:
    return not is_port_in_use(
        UnityEnvironment.BASE_ENVIRONMENT_PORT + worker_id
    )

def get_worker_id() -> int:
    pid = random.randrange(HIGHEST_WORKER_ID)
    while not is_worker_id_open(pid):
        print("Socket is occupied, trying a new worker_id")
        pid = random.randrange(HIGHEST_WORKER_ID)
    return pid

# Singleton equivalent for getting always one instance of both the environment and the side channel
def get_env(no_graphics = False, editor_mode = True, path_to_unity_exec : str = None, scene_number_to_load : int = 2):
    global env
    global channel
    pid = multiprocessing.Process()._identity[0]
    if (channel == None):
        channel = CustomSideChannel()

    if (env == None):
        # linux assumes cluster
        if platform == "linux" or platform == "linux2":
            if (editor_mode):
                env = UnityEnvironment(seed = 12, side_channels=[channel],no_graphics = True, worker_id=worked_id)
            else:
                worked_id = get_worker_id()
                print(f"Opening Unity, will try to use socket {worked_id} ({worked_id})")
                env = UnityEnvironment(file_name='linux_build/linux_build', seed = 12, side_channels=[channel],no_graphics = True, worker_id=worked_id)
        else:
            #print(f"Opening Unity, will try to use socket {pid + socket_number_offset + GLOBAL_SOCKET_OFFSET} ({pid}:{socket_number_offset}:{GLOBAL_SOCKET_OFFSET})")
            if (editor_mode):
                env = UnityEnvironment(seed = 12, side_channels=[channel],no_graphics = no_graphics) 
            else:
                env = UnityEnvironment(file_name=path_to_unity_exec + '\\ModularRobots', seed = 12, side_channels=[channel],no_graphics = no_graphics, worker_id=pid+ 1000 + GLOBAL_SOCKET_OFFSET) 
        if (env != None):
            print("Succesfully opened a new environment")
        print(f"Telling Unity to open scene number {scene_number_to_load}")
        channel.send_string(f"Scene:,{scene_number_to_load}")
        env.reset()
    return env, channel

def close_env():
    global env
    global channel
    if (env != None):
        env.close()
        env = None
        channel = None

def create_individual(env,side_channel,robot_graph, debug = False, record = False) -> list:
    
    # reset the environment
    env.reset()
       
    # transform the blueprint to JSON
    jsonfile = robot_graph.nodes_toJSON()
    if (debug):
        print(f"There are {len(robot_graph.nodes)} nodes in the robot graph")
        
    # send the blueprint
    side_channel.wait_for_robot_string = True
    side_channel.send_string(jsonfile)

    while side_channel.wait_for_robot_string:
        # unity waits a few frames before creating the robot (for determinism)
        env.step()

    if (side_channel.created_robot_module_keys is None):
        print(f"Could not find any controller information in the side channel")
    else:
        # Create a new controller list based on the controllers that were actually expressed
        created_module_keys = []
        for key in side_channel.created_robot_module_keys:    
            if key in robot_graph.nodes.keys():
                created_module_keys.append(key)

    if (debug):
        print(f"--- received keys:\n {side_channel.created_robot_module_keys}")
        print(f"--- stored keys:\n {robot_graph.nodes.keys()}")
        print(f"Controller list is of size {len(created_module_keys)}")

    # TODO: Prune robot graph, not working yet
    # robot_graph.prune(created_module_keys)
    
    # flush controllers (in case something was not deep copied)
    ns = decentralized_controller.innervate_modules(robot_graph)
    for key in robot_graph.controllers:
        robot_graph.innervation[key].flush()
    return created_module_keys

import emr.encoding.robot_graph as graph_utility
    
def evaluate_individual_in_simulation(robot_graph, created_module_keys, n_steps : int = 500, maximum_number_of_modules_allowed = 50, delta_time = 0.1,debug = False):
    fitness = -1
    # We assume there is only one individual in the simulation environment. 
    individual_name = list(env._env_specs)[0]
    behavior_spec = env.behavior_specs[individual_name];
    # Get the maximum number of allowed actions 
    action_size = behavior_spec[1].continuous_size

    # extract controllers
    controller_list = []
    for k in created_module_keys:
        controller_list.append(robot_graph.innervation[k])

    if (len(controller_list) >= maximum_number_of_modules_allowed):
        raise ValueError(f"too many modules created in the environment. Should be limited to {maximum_number_of_modules_allowed}")

    max_number_of_actions = action_size

    # contorller_to_key_dict = dict()
    # for c in controller_list:
    #    contorller_to_key_dict.update({c:})
    # should load scene and wait to receive string for individual
    for j in range(n_steps):
        obs,other = env.get_steps(individual_name)
        # update controllers to get actions
        actions = np.ndarray(shape=(1,max_number_of_actions),dtype=np.float32)
        sensory_inputs = np.ndarray(shape=(1,maximum_number_of_modules_allowed),dtype=np.float32)
        for i in range(len(obs.obs[0][0])):
            sensory_inputs[0][i] = obs.obs[0][0][i]
        
        graph_utility.forward_pass(robot_graph,controller_list)
        graph_utility.step_update_controllers(controller_list,sensory_inputs,actions,delta_time)

        # old version -------------------------:
        ## Indexing of modules!
        #for i,controller in enumerate(controller_list):
        #    if (i >= maximum_number_of_modules_allowed):
        #        if (j == 0):
        #            print(f"too many modules created in the environment. Should be limited to {maximum_number_of_modules_allowed}")
        #        break
        #    if (controller.fixed):
        #        action = controller.update(0.0)
        #    else:
        #        action = controller.update(0.1) * 1
        #    actions[0,i] = action      
        # -------------------------------------
        # send actions
        
        env.set_action_for_agent(individual_name,0,ActionTuple(actions))
        index = list(obs.agent_id_to_index)
        if (len(index)> 0):
            try:
                fitness = obs.reward[0]
                #print(fitness)
                #fitness = obs[index[0]][0][0][0]
                #print("fitness", fitness);
            except:
                print("Cannot get fitness")
                pass
        env.step()
    if (debug):
        print("[Python]: fitness = ",fitness)
    
    return fitness

def evaluate_individual(ind, executable_path : str, scene_number_to_load : int = 1, n_duplicates = 1, n_steps : int = 500, 
                        time_step : float = 0.01, no_graphics : bool = False, editor_mode : bool = False, debug : bool = False, record : bool = True) -> float:
    fitness = -1
    # n_duplicates is just to check duplicate fitness values when evaluating the same individual 
    # (should return the same fitness) TODO: add a test for this
    global env 
    global channel
    for _ in range(n_duplicates):
        # Get the singleton environment
    
        env, channel = get_env(path_to_unity_exec=executable_path,scene_number_to_load=scene_number_to_load, no_graphics= no_graphics, editor_mode=editor_mode)
        if (record):
            # Tell Unity to record this individual
            channel.send_string(f"Record,True,")
    
        robot_graph = ind.get_graph()
        ns = decentralized_controller.innervate_modules(robot_graph)
        # Reset the environment and make the robot
        created_module_keys = create_individual(env,channel,robot_graph=robot_graph, debug = debug, record = record)
        # Step through the simulation for the given number of steps 
        fitness = evaluate_individual_in_simulation(robot_graph = robot_graph,created_module_keys = created_module_keys, n_steps = n_steps, delta_time = time_step)
        if (record):
            # prompt Unity to return recording to python
            channel.send_string(f"Done")

    ind.fitness = fitness
    return fitness

def playback_recording_individual(ind, json_animation_of_individual : str, executable_path : str, scene_number_to_load : int = 1, n_duplicates = 1, n_steps : int = 500, 
                        time_step : float = 0.01, no_graphics : bool = False, editor_mode : bool = False, debug : bool = False) -> float:
    fitness = -1
    # n_duplicates is just to check duplicate fitness values when evaluating the same individual 
    # (should return the same fitness) TODO: add a test for this

    for _ in range(n_duplicates):
        # Get the singleton environment
        env, channel = get_env(path_to_unity_exec=executable_path,scene_number_to_load=scene_number_to_load, no_graphics= no_graphics, editor_mode=editor_mode)
        channel.send_string(f"Record,False,")
        robot_graph = ind.get_graph()
        ns = decentralized_controller.innervate_modules(robot_graph)
        channel.send_string(f"Playback,{json_animation_of_individual}")
        # Reset the environment and make the robot
        created_module_keys = create_individual(env,channel,robot_graph=robot_graph, debug = debug)
        # Step through the simulation for the given number of steps 
        fitness = evaluate_individual_in_simulation(robot_graph = robot_graph,created_module_keys = created_module_keys, n_steps = n_steps, delta_time = time_step)
        channel.send_string(f"Done")
    ind.fitness = fitness
    return fitness


def get_number_of_springs(robot_graph, robot_keys) -> int:
    count = 0
    for k in robot_keys:
        if (robot_graph.nodes[k].type == "LinearSpring"):
            count +=1
    return count

def evaluate_individual_multi_objective(ind, debug = False):
    # returns a dictionary with potential features of interest
    fitness = -1
    features = dict()
    # just to check duplicate fitness values
    for _ in range(1):
        robot_graph = ind.get_graph()
        created_module_keys = create_individual(robot_graph,debug)
        controller_list = []
        for k in created_module_keys:
            controller_list.append(robot_graph.controllers[k])
        fitness = evaluate_individual_in_simulation(robot_graph, controller_list)
        features.update({"number_of_modules":len(created_module_keys)})
        features.update({"number_of_springs":get_number_of_springs(robot_graph, created_module_keys)})
    combined_fitness = (fitness, features["number_of_springs"])
    return combined_fitness
    #return fitness, features
