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

    def __get_video_url(self, extension='mp4', resolution='480p'):
        # if best resolution is detected then return best video url
        if resolution == 'best':
            return [self.youtube_src.getbestvideo('mp4').url]
        # get all videos urls
        play = self.youtube_src.videostreams
        print(play)
        # create a valid videos map where :
        #           the key is video resolution (str)
        #           the value is list of videos urls on this resolution (list)
        valid_videos = {}
        # filter all videos urls depending on detected extension and all video at least with detected resolution
        for video in play:
            if video.extension == extension and video.dimensions[1] <= int(resolution[:-1]):
                if str(video.dimensions) in valid_videos.keys():
                    valid_videos[str(video.dimensions)].append(video)
                else:
                    valid_videos[str(video.dimensions)] = [video]
        # get highest video resolution from filtered videos urls
        highest_available_resolution = list(valid_videos.keys())[-1]
        # cast above videos urls as list
        valid_urls = [video.url for video in valid_videos[highest_available_resolution]]
        # return the result
        return valid_urls

    def __get_audio_url(self, extension='m4a', resolution=None):
        # if best audio depending on sample rate
        if resolution == 'best':
            return [self.youtube_src.getbestaudio('m4a').url]
        # get all audios urls
        play = self.youtube_src.audiostreams
        valid_urls = []
        for audio in play:
            if audio.extension == extension:
                valid_urls.append(audio.url)
        # return the result
        return valid_urls

    def receive(self, url):
        self.__set_src(url)
        #video_src = self.__get_video_url(resolution=str(self.video_config.height)+'p')
        try:
            video_src = self.__get_video_url(resolution=str(self.video_config.height) + 'p')
        except:
            print('No Video Config so 480p stream will received')
            video_src = self.__get_video_url(resolution='480p')
        audio_src = self.__get_audio_url()
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
