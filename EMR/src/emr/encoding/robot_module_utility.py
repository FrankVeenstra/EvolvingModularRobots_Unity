import random

MIN_ANGLE = -45
MAX_ANGLE = 45

# The y rotations of the ModularRobot3D approach.
modular_robot_angle_options = [[0,0,0],[0,90,0],[0,180,0],[0,270,0]]

def get_random_angle(module : str):
	if (module != 'SimsCube'):
		return random.choice(modular_robot_angle_options)
	else:
		#return [0,0,0]
		return [random.uniform(MIN_ANGLE,MAX_ANGLE),random.uniform(MIN_ANGLE,MAX_ANGLE),random.uniform(MIN_ANGLE,MAX_ANGLE)]
    
def mutate_angle(module : str,angle, sigma):
	if (module != 'SimsCube'):
		return random.choice(modular_robot_angle_options)
	else:
		#return angle
		for i in range(len(angle)):
			angle[i] = max(min(random.gauss(angle[i],sigma), MAX_ANGLE), MIN_ANGLE)
		return angle