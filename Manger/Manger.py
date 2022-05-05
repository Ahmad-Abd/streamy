from abc import ABC, abstractmethod


class Manger(ABC):
    @abstractmethod
    def serve_request(self, request):
        pass
