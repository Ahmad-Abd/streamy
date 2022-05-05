import subprocess
import json


class AudioStreamInfo:
    def __init__(self,
                 codec_name='aac',
                 sample_rate=44100,
                 channels=2,
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


class VideoStreamInfo:
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


def get_stream_info(url, stream_type='v', writer_mode='json'):
    command = ['ffprobe',
               '-show_format',
               '-show_streams',
               '-select_streams', stream_type,
               '-of', writer_mode,
               url]
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()
    if p.returncode != 0:
        print(error.decode('utf8'))
        return None
    # print(int(json.loads(output.decode('utf8'))['streams'][0]['time_base'][2:])/1000)
    if str.lower(stream_type) in ['a', 'audio']:
        audio_info = AudioStreamInfo()
        audio_info.from_json(json.loads(output.decode('utf8'))['streams'][0])
        return audio_info
    if str.lower(stream_type) in ['v', 'video']:
        video_info = VideoStreamInfo()
        video_info.from_json(json.loads(output.decode('utf8'))['streams'][0])
        return video_info


# url = 'inpujt.mp4'
# print(get_stream_info(url))
# print(get_stream_info(url, stream_type='a'))
