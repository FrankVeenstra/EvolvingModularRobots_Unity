import random
import math
import numpy as np
from emr.controller.abstract_controller import AbstractController
import abc

freq_options = [100]#[0.0,0.25,0.5,0.75,1.0,1.25,1.5,1.75,2.0,2.25,2.5] 


class CustomController(AbstractController):
	def __init__(self, hash_id = None, number_of_inputs : int = 0, number_of_outputs : int = 1):
		self.nodeid = hash_id # Debugging
		self.state = 0.0
		self.amp = 1
		self.freq = 0.1
		self.phase = 0
		self.offset = 0
		self.fixed = False
		self.number_of_inputs = number_of_inputs;
		self.number_of_outputs = number_of_outputs;

	def step(self, input_buffer, output_buffer, deltaTime):
		self.state += deltaTime
		output = []
		for i in range(self.number_of_outputs):
			#if (len(output_buffer) < i):
			output.append(self.amp * math.sin(self.freq * self.state + self.phase) + self.offset)
		return output
	
	def forward_pass(self):
		pass
	
	def print(self):
		return "~"

	def flush(self):
		self.state = 0

	@staticmethod
	def random(id = None,number_of_inputs = 0, number_of_outputs= 1):
		c = CustomController(id, number_of_inputs=number_of_inputs,number_of_outputs=number_of_outputs)
		c.amp = random.uniform(-1.0,1.0)
		c.freq = random.choice(freq_options)
		c.phase = random.uniform(-1.0,1.0)
		c.offset = random.uniform(-1,1)
		c.ascending_weights = [random.uniform(-1,1)]
		c.descending_weights = [random.uniform(-1,1)]
		return c
	
	def mutate(self,mutation_rate, mutation_sigma):
		if (random.uniform(0,1)< mutation_rate):
			self.amp = np.clip(random.gauss(self.amp, mutation_sigma),-1,1)
		if (random.uniform(0,1)< mutation_rate):
			self.phase = np.clip(random.gauss(self.phase, mutation_sigma),-1,1)
		if (random.uniform(0,1)< mutation_rate):
			self.offset = np.clip(random.gauss(self.offset, mutation_sigma),-1,1)
		if (random.uniform(0,1)< mutation_rate):
			self.freq = random.choice(freq_options)
		

