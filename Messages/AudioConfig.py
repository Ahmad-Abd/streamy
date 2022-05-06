from Messages.Message import Message


class AudioConfig(Message):
    def __init__(self,
                 codec_name='aac',
                 sample_rate=44100,
                 channels=1,
                 bit_rate=-1):
        self.codec_name = codec_name
        self.sample_rate = sample_rate
        self.channels = channels
        self.bit_rate = bit_rate

    def from_json(self, json_object):
        self.codec_name = json_object['codec_name']
        self.sample_rate = json_object['sample_rate']
        self.channels = json_object['channels']
        try:
            self.bit_rate = json_object['bit_rate']
        except:
            self.bit_rate = None

    def __str__(self):
        return f'codec : {self.codec_name}, ' \
               f'sample rate : {self.sample_rate}, ' \
               f'channels : {self.channels}, ' \
               f'bit rate : {self.bit_rate}'
