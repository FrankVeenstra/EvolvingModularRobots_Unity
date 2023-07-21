import uuid

class Nerve:
	def __init__(self, index, value):
		self.index = index
		self.value = value


class DecentralizedController:
    def __init__(self, controller, module_id : str = None):
        if (module_id == None):
            self.id = uuid.uuid4()
        else:
            self.id = module_id
        self.controller = controller
        self.parents = dict()
        self.children = dict()
        # self.inputs = dict()
        self.input_buffer = []
        self.output_buffer = []

        self.ascending_weights = [0.0]
        self.descending_weights = [0.0]

        # start with one input and output buffer representing one sensor and one actuator
        for i in range(controller.number_of_inputs):
            self.input_buffer.append(0)
        for i in range(controller.number_of_outputs):
            self.output_buffer.append(0)
        pass

    def step(self, sensory_input, actuator_output, delta_time):
        for i in range(len(sensory_input)):
            if (i >= len(self.input_buffer)):
                break
            self.input_buffer[i] = sensory_input[i]
        self.output_buffer = self.controller.step(self.output_buffer, self.input_buffer, delta_time)
        for i in range(len(actuator_output)):
            actuator_output[i] = self.output_buffer[i]
        return actuator_output

    def forward_pass(self, index, value : float):
        # the robot_graph forward pass function looks at the nerves and calls forward pass on every connection. value is the output of the nerve. 
        self.input_buffer[index] = value
        # pass on input_buffer to control module
        # self.controller.forward_pass(self.input_buffer)

    def flush(self):
        if (self.controller != None):
            self.controller.flush()
        for i in range(len(self.input_buffer)):
            self.input_buffer[i] = 0.0
        for i in range(len(self.output_buffer)):
            self.output_buffer[i] = 0.0

    def _add_parent_nerve(self, other, value : float):
        index = len(other.input_buffer)
        self.parents.update({other.id: Nerve(index, value)})
        # other.inputs.update({self.id:len(other.inputs)-1})
        other.input_buffer.append(0.0)
        self.output_buffer.append(0.0)

    def _add_child_nerve(self,other, value : float):
        index = len(other.input_buffer)
        self.children.update({other.id: Nerve(index, value)})
        #other.inputs.update({self.id:})
        other.input_buffer.append(0.0)
        self.output_buffer.append(0.0)

    def __add__(self,other):
        self._add_child_nerve(other, self.descending_weights[0])
        other._add_parent_nerve(self, self.ascending_weights[0])
        return other

def innervate_modules(blueprint):
    innervation = dict()
    queue = ['root']
    innervation.update({queue[0]:DecentralizedController(blueprint.controllers[queue[0]], queue[0])})

    while len(queue) > 0:
        cid = queue.pop(0)
        for c in blueprint.get_children(cid, blueprint.nodes):
            queue.append(c)
            innervation.update({c:innervation[blueprint.nodes[c].parent] + DecentralizedController(blueprint.controllers[c], c)})

    blueprint.innervation = innervation
    pass 


