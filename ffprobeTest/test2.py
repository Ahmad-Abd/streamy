from pafy import pafy
import time
import itertools
import ffmpeg
from test import get_stream_info
from Receiver.ReceiverFactory import ReceiverFactory
t = time.time()
# url = 'https://youtu.be/-GHCmtjiygw'
url = 'https://youtu.be/zT_gG1Uv-ps'
def get_src(url):
    vPafy = pafy.new(url)
def get_video_url(url, extension=['mp4'], resolution='720p'):
    vPafy = pafy.new(url)
    if resolution == 'best':
        return vPafy.getbestvideo('mp4')
    play = vPafy.videostreams
    valid_videos = {}
    for video in play:
        if video.extension in extension and video.dimensions[1] <= int(resolution[:-1]):
            if str(video.dimensions) in valid_videos.keys():
                valid_videos[str(video.dimensions)].append(video)
            else:
                valid_videos[str(video.dimensions)] = [video]
    highest_available_resolution = list(valid_videos.keys())[-1]
    l = [(video.url, get_stream_info(video.url)) for video in valid_videos[highest_available_resolution]]
    '''
    for i in l:
        print('url :', i[0])
        print('info :', i[1])
        print('\n\n')
    '''
def get_audio_url(url):
    vPafy = pafy.new(url)
    print(type(vPafy))
    play = vPafy.audiostreams
    play2 = vPafy.videostreams
    play3 = vPafy.streams
    print(play)
    l = [(audio , audio.url, get_stream_info(audio.url,stream_type='a')) for audio in play]
    for i in l:
        print('audio :', i[0])
        print('url :', i[1])
        print('info :', i[2])
        print('\n\n')
    #print(play2)
    #print(play3)
get_audio_url(url)
#get_video_url(url, resolution='480p')
print(time.time() - t)
