from abc import ABC, abstractmethod


class Sender(ABC):
    @abstractmethod
    def __init__(self):
        self.audio_config = None
        self.video_config = None
        self.translate_config = None

    @abstractmethod
    def send(self,url):
        pass

    def set_config(self, audio_config, video_config):
        self.audio_config = audio_config
        self.video_config = video_config
