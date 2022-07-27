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


# config
#stream_url = 'https://youtu.be/spUNpyF58BY'
stream_url = 'https://youtu.be/Gd6RVwRmt9w'
rtmp_server_url = 'rtmp://a.rtmp.youtube.com/live2/'
rtmp_server_key = '3wgb-cv03-ckyy-jmxc-cw42'
audio_config = AudioConfig()
video_config = None
translation_config = None

# build the request
request_example = StreamyFormRequest(
    stream_url=stream_url,
    rtmp_server_url=rtmp_server_url,
    rtmp_server_key=rtmp_server_key,
    audio_config=audio_config,
    video_config=video_config,
    secure_mode=False)

# define the manger
manger = StreamyManger()

manger.serve_request(request=request_example)
