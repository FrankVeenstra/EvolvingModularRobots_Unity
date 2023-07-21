from abc import (
  ABC,
  abstractmethod,
)

class AbstractController(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def forward_pass(self):
        raise NotImplementedError()

    @abstractmethod
    def step(self):
        raise NotImplementedError()

    @abstractmethod
    def flush(self):
        raise NotImplementedError()

    @abstractmethod
    def random(id = None,number_of_inputs = 0, number_of_outputs= 1):
        raise NotImplementedError()

    @abstractmethod
    def mutate(self, mutation_rate : float, mutation_sigma : float):
        raise NotImplementedError()

