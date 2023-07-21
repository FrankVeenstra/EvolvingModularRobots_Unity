

# possible class for paleobot
class PaleobotEncoding:
	def __init__(self, controller_reference, config, fitness = -1.0):
		self.module_options = ch.modules_to_use()
		self.fitness = fitness

		self.isDirty = True

		self.controller_reference = controller_reference
		self.genome = robot;

	@staticmethod 
	def random():
		individual = PaleobotEncoding()
		return individual