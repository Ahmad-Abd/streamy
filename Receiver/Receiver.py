from abc import ABC, abstractmethod
from Utilities import FFmpegWrapper

class Receiver(ABC):
    @abstractmethod
    def __init__(self):
        self.audio_config = None
        self.video_config = None
        self.translate_config = None
        self.raw_video = None
        self.raw_audio = None

    @abstractmethod
    def receive(self,url):
        pass

    def set_config(self, audio_config, video_config):
        self.audio_config = audio_config
        self.video_config = video_config
