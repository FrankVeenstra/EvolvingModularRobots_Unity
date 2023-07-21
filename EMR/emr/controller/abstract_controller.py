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