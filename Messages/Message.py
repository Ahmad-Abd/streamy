from abc import ABC, abstractmethod


class Message(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def from_json(self, json_object):
        pass
