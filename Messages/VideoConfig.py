from Messages.Message import Message


class VideoConfig(Message):
    def __init__(self,
                 codec_name='None',
                 fps=30,
                 width=640,
                 height=360,
                 bit_rate=-1):
        self.codec_name = codec_name
        self.fps = fps
        self.width = width
        self.height = height
        self.bit_rate = bit_rate

    def from_json(self, json_object):
        self.codec_name = json_object['streams'][0]['codec_name']
        a = int(json_object['streams'][0]['r_frame_rate'].split('/')[0])
        b = int(json_object['streams'][0]['r_frame_rate'].split('/')[1])
        self.fps = round(a/b)
        try:
            self.bit_rate = json_object['format']['bit_rate']
        except Exception as e:
            self.bit_rate = None

    def __str__(self):
        return f'codec : {self.codec_name}, ' \
               f'fps : {self.fps}, ' \
               f'width : {self.width}, ' \
               f'height :  {self.height}, ' \
               f'bit rate : {self.bit_rate} bit/s'
