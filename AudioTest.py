from Manger.StreamyManger import StreamyManger
from Messages.AudioConfig import AudioConfig
from Messages.StreamyFormRequest import StreamyFormRequest
from Messages.VideoConfig import VideoConfig
from ProcessingSystems.AudioProcessingSystem.ThresholdingBasedAudioDenoiser.ThresholdBasedAudioDenoiser import ThresholdBasedAudioDenoiser
from Receiver.ReceiverFactory import ReceiverFactory
from Manger.Manger import Manger
from Sender.SenderFactory import SenderFactory
from Utilities.FFmpegWrapper import *
import numpy as np

stream_url = 'https://youtu.be/Y0ErYtveYuE'

#rtmp_server_url = 'rtmp://a.rtmp.youtube.com/live2/'
#rtmp_server_key = '3wgb-cv03-ckyy-jmxc-cw42'
rtmp_server_url = 'rtmps://dc4-1.rtmp.t.me/s/'
rtmp_server_key = '1655497746:ZFlNeq75gPbZIdYY3DL81w'

audio_config = AudioConfig(sample_rate=16000,block_size=1024,channels=1,dtype=np.int16)
video_config = None

request_example = StreamyFormRequest(
    stream_url=stream_url,
    rtmp_server_url=rtmp_server_url,
    rtmp_server_key=rtmp_server_key,
    audio_config=audio_config,
    video_config=video_config,
    secure_mode=False,
    aps_type='psd',
    vps_type='selfie')

manger = StreamyManger()

manger.serve_request(request=request_example)
