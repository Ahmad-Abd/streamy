from abc import ABC, abstractmethod


class Sender(ABC):
    @abstractmethod
    def __init__(self):
        self.audio_config = None
        self.video_config = None
        self.request = None
        self.dst = None

    @abstractmethod
    def send(self):
        pass

    def set_config(self, request):
        self.request = request
        self.audio_config = request.audio_config
        self.video_config = request.video_config
        self.dst = None
