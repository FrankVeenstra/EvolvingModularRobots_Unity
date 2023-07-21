import random
import math
import numpy as np
from emr.controller.abstract_controller import AbstractController
import abc

freq_options = [1]#[0.0,0.25,0.5,0.75,1.0,1.25,1.5,1.75,2.0,2.25,2.5] 


class CustomController(AbstractController):
	def __init__(self, hash_id = None):
		self.nodeid = hash_id # Debugging
		self.state = 0.0
		self.amp = 1
		self.freq = 0.5
		self.phase = 0
		self.offset = 0
		self.fixed = False
		self.number_of_inputs = 0
		self.number_of_outputs = 0

	def step(self, input_buffer, output_buffer, deltaTime):
		self.state += deltaTime
		for i in range(len(input_buffer)):
			if (len(output_buffer) < i):
				output_buffer[i] = self.amp * math.sin(self.freq * self.state + self.phase) + self.offset
		return output_buffer
	
	def forward_pass(self):
		pass
	
	def print(self):
		return "~"

	def flush(self):
		self.state = 0

	@staticmethod
	def random(id = None):
		c = CustomController(id)
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
		
if __name__ == "__main__":
	import matplotlib.pyplot as plt
	d = []
	controller = CustomController()
	for i in range(100):
		d.append(controller.update())
	plt.plot(d)
