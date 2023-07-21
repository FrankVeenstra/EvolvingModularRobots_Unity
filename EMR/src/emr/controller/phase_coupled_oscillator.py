import random
import math
from emr.controller.abstract_controller import AbstractController
from emr.evolution import ea_utility as utility


# This class is contained in the decentralized controller class
class PhaseCoupledOscillator(AbstractController):
	def __init__(self, frequency : float, amplitude : float, vertical_offset : float, desired_phase_difference : float, number_of_inputs : int,number_of_outputs : int):
		# range [-1,1]
		self.frequency = frequency;
		self.amplitude = amplitude;
		self.desired_joint_angle = 0.0;
		self.desired_phase_difference = desired_phase_difference;
		self.connections = []
		self.phi = 0
		self.attraction_coefficient = 1.0
		self.vertical_offset = vertical_offset
		self.number_of_inputs = number_of_inputs;
		self.number_of_outputs = number_of_outputs;

	def flush(self):
		self.phi = 0.0
		self.desired_joint_angle = 0.0
		self.input = 0.0

	def mutate(self,mutation_rate, mutation_sigma):
		self.amplitude = utility.mutate_value(self.amplitude, mutation_rate,mutation_sigma)
		self.frequency = utility.mutate_value(self.frequency, mutation_rate,mutation_sigma)
		self.vertical_offset = utility.mutate_value(self.vertical_offset, mutation_rate,mutation_sigma)
	
	@staticmethod
	def random(id = None, number_of_inputs = 1, number_of_outputs = 1):
		f = random.uniform(-1,1)
		a = random.uniform(-1,1)
		v = random.uniform(-1,1)
		dp = random.uniform(-1,1)
		instance = PhaseCoupledOscillator(f, a, v, dp, number_of_inputs, number_of_outputs)
		instance.type = type
		return instance

	def step(self, input_buffer, output_buffer,delta_time : float):
		# desired phase offset is the accummulation of the input * PI
		summed_input = sum(input_buffer)
		delta_time = 0.1
		inputBasedOnDesiredPhaseDifference = (self.desired_phase_difference + summed_input) 
		outputs = []
		self.phi += (math.tau * self.frequency * delta_time * inputBasedOnDesiredPhaseDifference)
		self.desired_joint_angle = self.amplitude * math.sin(self.phi) + self.vertical_offset 
		for i in range(self.number_of_outputs):
			outputs.append(self.desired_joint_angle)
		return outputs

	def print(self):
		return "pco"

	# ---------- TEMP ----------------
	def forward_pass(self):
		print("Should not call forward pass on PhaseCoupledOscillator")
		# below is old. For temporary reference
		for c in self.connections:
			if (c.target is not None):
				a = math.pi * c.weight * math.sin(self.phi - c.target.phi - c.desired_phase_difference)
				# simulating downstream connections
				c.target.input += a;
	# --------------------------------
