from Messages.Message import Message
import numpy as np

class AudioConfig(Message):
    def __init__(self,
                 codec_name='None',
                 sample_rate=44100,
                 block_size=2048,
                 dtype = np.int16,
                 channels=1,
                 bit_rate=-1):
        self.codec_name = codec_name
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.channels = channels
        self.dtype = dtype
        self.bit_rate = bit_rate

    def from_json(self, json_object):
        self.codec_name = json_object['streams'][0]['codec_name']
        self.sample_rate = json_object['streams'][0]['sample_rate']
        self.channels = json_object['streams'][0]['channels']
        try:
            self.bit_rate = json_object['format']['bit_rate']
        except:
            self.bit_rate = None

    def __str__(self):
        return f'codec : {self.codec_name}, ' \
               f'sample rate : {self.sample_rate}, ' \
               f'channels : {self.channels}, ' \
               f'bit rate : {self.bit_rate} bit/s'
