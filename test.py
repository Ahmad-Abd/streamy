'''
TEST Example 
'''
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

# config
#stream_url = 'https://youtu.be/spUNpyF58BY'
#stream_url = 'https://youtu.be/Gd6RVwRmt9w'
# cc to world
stream_url = 'https://youtu.be/J7GY1Xg6X20'
# bbc live
stream_url = 'https://youtu.be/HxI2TxhhS9A'
rtmp_server_url = 'rtmp://a.rtmp.youtube.com/live2/'
rtmp_server_key = '3wgb-cv03-ckyy-jmxc-cw42'
audio_config = AudioConfig(sample_rate=44100,block_size=2048,channels=1,dtype=np.int16)
video_config = None
translation_config = None

# build the request
request_example = StreamyFormRequest(
    stream_url=stream_url,
    rtmp_server_url=rtmp_server_url,
    rtmp_server_key=rtmp_server_key,
    audio_config=audio_config,
    video_config=video_config,
    secure_mode=False,
    aps_type='threshold',
    vps_type='selfie')

# define the manger
manger = StreamyManger()

manger.serve_request(request=request_example)
