from Messages.Message import Message


class VideoConfig(Message):
    def __init__(self,
                 codec_name='h264',
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
        self.codec_name = json_object['codec_name']
        self.fps = int(int(json_object['r_frame_rate'].split('/')[0]))
        if self.fps // 1000 != 0:
            self.fps //= 1000
        elif self.fps // 100 != 0:
            self.fps //= 100
        self.width = json_object['width']
        self.height = json_object['height']
        try:
            self.bit_rate = json_object['bit_rate']
        except:
            self.bit_rate = None

    def __str__(self):
        return f'codec : {self.codec_name}, ' \
               f'fps : {self.fps}, ' \
               f'width : {self.width}, ' \
               f'height :  {self.height}, ' \
               f'bit rate : {self.bit_rate}'
