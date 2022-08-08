from ProcessingSystems.AudioProcessingSystem.ThresholdingBasedAudioDenoiser.ThresholdBasedAudioDenoiser import ThresholdBasedAudioDenoiser
from ProcessingSystems.AudioProcessingSystem.PsdEstimationBasedAudioDenoiser.PsdEstimationBasedAudioDenoiser import PsdEstimationBasedAudioDenoiser
from ProcessingSystems.AudioProcessingSystem.DemucsBasedAudioDenoiser.DemucsBasedAudioDenoiser import DemucsBasedAudioDenoiser
from ProcessingSystems.VideoProcessingSystems.SelfieSegmetationBasedCAE import SelfieSegmetationBasedCAE
from Receiver.ReceiverFactory import ReceiverFactory
from Manger.Manger import Manger
from Sender.SenderFactory import SenderFactory
from Utilities.FFmpegWrapper import *
from ffprobeTest.test import *
import numpy as np

class StreamyManger(Manger):
    # create a ReceiverFactory as a static object
    RECEIVER_FACTORY = ReceiverFactory()

    # create a SenderFactory as a static object
    SENDER_FACTORY = SenderFactory()

    # Define Supported Video and Audio Codec
    SUPPORTED_AUDIO_CODEC = ['aac']
    SUPPORTED_VIDEO_CODEC = ['h264']

    def __get_aps(self,aps_type):
        """
        Create an AudioProcessingSystem depending on processing method type
        :param aps_type:str type of Audio Processing System valid types ['threshold','psd','demucs']
        :return: object of ProcessingSystem
        """
        if aps_type == 'threshold':
            print('\n\033[1;94mInitializing Threshold Based Audio Denoiser...\033[0m')
            return ThresholdBasedAudioDenoiser(threshold=10)
        if aps_type == 'psd':
            print('\n\033[1;94mInitializing PSD Estimation Based Audio Denoiser...\033[0m')
            return PsdEstimationBasedAudioDenoiser(threshold=0.001,
                                                   fs = 16000,
                                                   block_size=1024,
                                                   time_smoothing_constant=0.2)
        if aps_type == 'demucs':
            print('\n\033[1;94mInitializing Demucs Based Audio Denoiser...\033[0m')
            return DemucsBasedAudioDenoiser()
        print('\033[1;91m[Error] Not Supported Audio Processing System....\033[0m')
        exit(-1)

    def __get_vps(self,vps_type):
        """
        Create a VideoProcessingSystem depending on processing method type
        :param vps_type:str type of Video Processing System valid types ['selfie','motion']
        :return: object of ProcessingSystem
        """
        print(vps_type)
        if vps_type == 'selfie':
            print('\n\033[1;94mInitializing Selfie Segmentation Based CAE...\033[0m')
            return SelfieSegmetationBasedCAE()
        '''
        if vps_type == 'motion':
            print('Initializing Motion Based CAE...')
            return PsdEstimationBasedAudioDenoiser()
        '''
        print('\033[1;91m[Error] Not Supported Video Processing System....\033[0m')
        exit(-1)

    def __get_processing_system(self, request):
        """
        Create either Video or Audio Processing System depending on request video and aduio config
        :param request: Message  the received request from the user
        :return: object of ProcessingSystem
        """
        # define a null processing_system and chunk_size
        processing_system, chunk_size = None, None
        # check if video config in the request in not none then create and vps using __get_vps()
        if request.video_config:
            print('\n\033[1;32mVideo Processing Mode...\033[0m')
            # create the vps using __get_vps()
            processing_system = self.__get_vps(request.vps_type)
            assert processing_system is not None,exit(-1)
            # set requests video config in the created vps
            processing_system.resize(request.video_config.width ,request.video_config.height)
            # chunk_size is equal to size of image * 3 is number of channels
            chunk_size = request.video_config.width * request.video_config.height * 3
        # check if audio config in the request in not none then create and aps using __get_aps()
        elif request.audio_config:
            print('\n\033[1;32mAudio Processing Mode...\033[0m')
            # create the aps using __get_aps()
            processing_system = self.__get_aps(request.aps_type)
            assert processing_system is not None, exit(-1)
            # set requests audio config in the created aps
            processing_system.fs = request.audio_config.sample_rate
            processing_system.block_size = request.audio_config.block_size
            processing_system.sample_type = request.audio_config.dtype
            processing_system.channels = request.audio_config.channels
            size_of_sample_in_bytes = np.dtype(request.audio_config.dtype).itemsize
            # chunk_size is equal to size of sample ber bytes * number of samples in block
            chunk_size = processing_system.block_size * size_of_sample_in_bytes
        else:
            # not detected config in the request
            print('\033[1;91m[Error] Not Detected Config....\033[0m')
            exit(-1)
        # return the result
        return processing_system, chunk_size

    def __select_url(self, urls, stream_type ='v'):
        """
        Filter The Audio and Video URLs depending on supported video and audio codec in our system
        :param urls: list of audio or video urls to filter
        :return:
        """
        for url in urls:
            try:
                url_stream_info = get_stream_info(url, stream_type=stream_type)
                if stream_type == 'v':
                    if url_stream_info.codec_name in StreamyManger.SUPPORTED_VIDEO_CODEC:
                        print(f'\033[1mInput Video Stream Info => {url_stream_info}\033[0m\n')
                        return url ,url_stream_info
                elif stream_type == 'a':
                    if url_stream_info.codec_name in StreamyManger.SUPPORTED_AUDIO_CODEC:
                        print(f'\033[1mInput Audio Stream Info => {url_stream_info}\033[0m')
                        return url ,url_stream_info
                else:
                    # not detected config in the request
                    print('\033[1;91m[Error] Not Detected Config....\033[0m')
                    exit(-1)
            except:
                print('Error in get_info')
                continue
        print('\033[1;91m[Error] Streams Codec Are Not Supported....\033[0m')
        exit(-1)

    def serve_request(self, request):
        # 1. Create (APS or VPS) Depending on Request
        processing_system, chunk_size = self.__get_processing_system(request)
        print('\n\033[1;94mDone...\033[0m')

        # 2. Create Receiver using Receiver Factory Depending on Request URL
        receiver = StreamyManger.RECEIVER_FACTORY.get_receiver(url=request.stream_url)
        receiver.set_config(request=request)

        # 3. Create Sender using Sender Factory Depending on Request URL
        sender = StreamyManger.SENDER_FACTORY.get_sender(url=request.rtmp_server_url)
        sender.set_config(request=request)

        # Streamy Serve Pipeline: Receive -> Process -> Send
        audio_src, video_src = None, None
        destination_url = None
        try:
            # get audio and video sources from the receiver
            audio_src, video_src = receiver.receive(url=request.stream_url)
            # get the destination url from the sender
            destination_url = sender.send()
        except Exception as e:
            print(e)
            exit(-1)
        # create a decoding process as None
        decoding_process = None
        # create a encoding process as None
        encoding_process = None
        # filter video urls depending on supported codec
        video_src ,input_video_src_config = self.__select_url(video_src)
        # filter audio urls depending on supported codec
        audio_src ,input_audio_src_config = self.__select_url(audio_src, stream_type='a')
        # if Audio Config is detected in the received request then create a decode and encode audio processes
        if request.audio_config:
            # create the decoding audio process
            decoding_process = decode_audio(audio_src=audio_src,
                                            dst_audio_config=request.audio_config,
                                            src_audio_config=input_audio_src_config)
            # create the encoding audio process
            encoding_process = encode_audio(video_src=video_src,
                                            dst_audio_config=request.audio_config,
                                            src_audio_config=input_audio_src_config,
                                            dst=destination_url)
        # else if Audio Config is detected in the received request then create a decode and encode audio processes
        elif request.video_config:
            # create the decoding video process
            decoding_process = decode_video(video_src=video_src,
                                            dst_video_config=request.video_config,
                                            src_video_config=input_video_src_config)
            # create the decoding video process
            encoding_process = encode_video(audio_src=audio_src,
                                            dst_video_config=request.video_config,
                                            src_video_config=input_video_src_config,
                                            dst=destination_url)
        # attach process to sender and receiver!!!!!!!!!!!!!!!!
        # untreated raw data is the decoding process stdout
        untreated_raw_data_stdout = decoding_process.stdout
        treated_raw_data_stdin = encoding_process.stdin
        while True:
            # read data from the receiver stdout pipe
            untreated_data_chunk = untreated_raw_data_stdout.read(chunk_size)
            # check about if it is not none
            if untreated_data_chunk:
                # process data using processing system
                treated_data_chunk = processing_system.process(untreated_data_chunk)
                # write processed data to the sender stdin pipe
                treated_raw_data_stdin.write(treated_data_chunk)