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

#stream_url = 'https://youtu.be/4WSCQwf1Sr8'
#stream_url = 'https://youtu.be/_8cXEqa78IQ'
#stream_url = 'https://youtu.be/1gB5NrCT5hY'
stream_url = 'https://youtu.be/_8cXEqa78IQ'

#rtmp_server_url = 'rtmp://a.rtmp.youtube.com/live2/'
#rtmp_server_key = '3wgb-cv03-ckyy-jmxc-cw42'
rtmp_server_url = 'rtmp://fra02.contribute.live-video.net/app/'
rtmp_server_key = 'live_815948102_BMGI6RZinvv2fWN3Su35Y7B55U4wS1'
audio_config = None
video_config = VideoConfig(width=854,height=480)

request_example = StreamyFormRequest(
    stream_url=stream_url,
    rtmp_server_url=rtmp_server_url,
    rtmp_server_key=rtmp_server_key,
    audio_config=audio_config,
    video_config=video_config,
    secure_mode=False,
    aps_type='demucs',
    vps_type='selfie')

manger = StreamyManger()

manger.serve_request(request=request_example)
