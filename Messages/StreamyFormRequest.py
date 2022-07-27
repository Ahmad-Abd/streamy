from Messages.Message import Message


class StreamyFormRequest(Message):

    def __init__(self,
                 stream_url,
                 rtmp_server_url,
                 rtmp_server_key,
                 audio_config,
                 video_config,
                 aps_type='threshold',  # threshold ,psd ,demucs
                 vps_type='selfie',  # selfie ,motion
                 secure_mode=False,
                 block_audio=False,
                 block_video=False
                 ):
        self.rtmp_server_url = rtmp_server_url
        self.rtmp_server_key = rtmp_server_key
        self.secure_mode = secure_mode
        self.stream_url = stream_url
        self.video_config = video_config
        self.audio_config = audio_config
        self.block_audio = block_audio
        self.block_video = block_video
        self.aps_type = aps_type
        self.vps_type = vps_type

    def from_json(self, json_object):
        pass
