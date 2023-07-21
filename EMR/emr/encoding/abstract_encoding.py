from abc import (
  ABC,
  abstractmethod,
)

class AbstractEncoding(ABC):
    def __init__(self):
        pass

    
    # For generating random individuals
    @abstractmethod
    def random():
        raise NotImplementedError()

    @abstractmethod
    def mutate(morphology_mutation_probability, controller_mutation_probability, mutation_spread):
        raise NotImplementedError()

    @abstractmethod
    def get_graph():
        raise NotImplementedError()

    @abstractmethod
    def save(individual, target_directory : str, filename : str):
        raise NotImplementedError

    @abstractmethod
    def load(target_directory : str, filename : str):
        raise NotImplementedError
