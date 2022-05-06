import ffmpeg
from pafy import pafy
from Exceptions.Exceptions import *
from Receiver.Receiver import Receiver
from ffprobeTest.test import get_stream_info
from Utilities.FFmpegWrapper import *


class YoutubeReceiver(Receiver):
    def __init__(self):
        super().__init__()
        self.youtube_src = None

    def __set_src(self, url):
        try:
            self.youtube_src = pafy.new(url)
        except Exception as e:
            print(e)
            return None

    def get_video_url(self, extension='mp4', resolution='720p'):
        if resolution == 'best':
            # get info for 'https://www.youtube.com/watch?v=D2zMc5Fw4m0' videostreams[9] if found only r_frame_rate
            # what if mp4 is Not available !!!!!!!!!!
            return [self.youtube_src.getbestvideo('mp4').url]
        play = self.youtube_src.videostreams
        valid_videos = {}
        for video in play:
            if video.extension == extension and video.dimensions[1] <= int(resolution[:-1]):
                if str(video.dimensions) in valid_videos.keys():
                    valid_videos[str(video.dimensions)].append(video)
                else:
                    valid_videos[str(video.dimensions)] = [video]
        highest_available_resolution = list(valid_videos.keys())[-1]
        valid_urls = [video.url for video in valid_videos[highest_available_resolution]]
        return valid_urls

    def get_audio_url(self, extension='m4a', resolution=None):
        if resolution == 'best':
            return [self.youtube_src.getbestaudio('m4a').url]
        play = self.youtube_src.audiostreams
        valid_urls = []
        for audio in play:
            if audio.extension == extension:
                valid_urls.append(audio.url)
        return valid_urls

    def receive(self, url):
        self.__set_src(url)
        video_src = self.get_video_url()
        audio_src = self.get_audio_url()
        if len(video_src) == 0 or len(audio_src) == 0:
            raise ReceivingURLNotFoundException()
        return audio_src, video_src
        '''
        if self.audio_config:
            # receive and decode audio
            return audio_receive_decode(audio_src=audio_src,audio_config=self.audio_config), video_src
        elif self.video_config:
            return

        input_stream = ffmpeg.input(url)
        # Get the compressed audio from stream
        compressed_audio_input_stream = input_stream['a']
        # Get the compressed video from stream
        compressed_video_input_stream = input_stream['v']
        # Define the raw audio stream form
        raw_audio_input = ffmpeg.output(
            compressed_audio_input_stream,
            'pipe:',
            format='s16le',
            ac='2',
            sample_rate='44100'
        )
        # Run the compressed audio decoding process
        audio_decoding_process = ffmpeg.run_async(raw_audio_input, pipe_stdout=True)
        raw_audio_stream = audio_decoding_process.stdout
        # Define the raw video stream form
        raw_video_input = ffmpeg.output(
            compressed_video_input_stream,
            'pipe:',
            hwaccel='nvdec',
            format='rawvideo',
            pix_fmt='bgr24',
        )
        # Run the compressed audio decoding process
        video_decoding_process = ffmpeg.run_async(raw_video_input, pipe_stdout=True)
        raw_video_stream = video_decoding_process.stdout
        pass
        '''
