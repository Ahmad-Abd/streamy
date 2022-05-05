from abc import ABC, abstractmethod


class ProcessingSystem(ABC):
    @abstractmethod
    def process(self,block):
        pass