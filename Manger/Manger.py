from abc import ABC, abstractmethod


class Manger(ABC):
    """
    An abstract class to manage AI-Powered Streaming Server
    for re-use or define a custom Manging Pipeline just re-implement server_request(request) function
    be aware about your Request from which subclass of Message
    for more details see:
    StreamyManger ,SteamyFormRequest
    """
    @abstractmethod
    def serve_request(self, request):
        pass
