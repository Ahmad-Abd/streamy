from ProcessingSystems.AudioProcessingSystem.ThresholdingBasedAudioDenoiser.ThresholdBasedAudioDenoiser import ThresholdBasedAudioDenoiser
from ProcessingSystems.AudioProcessingSystem.PsdEstimationBasedAudioDenoiser.PsdEstimationBasedAudioDenoiser import PsdEstimationBasedAudioDenoiser
from ProcessingSystems.AudioProcessingSystem.DemucsBasedAudioDenoiser.DemucsBasedAudioDenoiser import DemucsBasedAudioDenoiser
from ProcessingSystems.VideoProcessingSystems.SelfieSegmetationBasedCAE import SelfieSegmetationBasedCAE
from Receiver.ReceiverFactory import ReceiverFactory
from Manger.Manger import Manger
from Sender.SenderFactory import SenderFactory
from Utilities.FFmpegWrapper import *
from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np
pd.read_csv()
np.reshape()
LinearRegression().fit()
class StreamyManger(Manger):
    # create a ReceiverFactory as a static object
    receiver_factory = ReceiverFactory()

    # create a SenderFactory as a static object
    sender_factory = SenderFactory()

    def __get_aps(self,aps_type):
        """
        Create an AudioProcessingSystem depending on processing method type
        :param aps_type:str type of Audio Processing System valid types ['threshold','psd','demucs']
        :return: object of ProcessingSystem
        """
        if aps_type == 'threshold':
            print('Initializing Threshold Based Audio Denoiser...')
            return ThresholdBasedAudioDenoiser()
        if aps_type == 'psd':
            print('Initializing PSD Estimation Based Audio Denoiser...')
            return PsdEstimationBasedAudioDenoiser()
        if aps_type == 'demucs':
            print('Initializing Demucs Based Audio Denoiser...')
            return DemucsBasedAudioDenoiser()
        print('[Error] Not Supported APS....')
        exit(-1)

    def __get_vps(self,vps_type):
        """
        Create a VideoProcessingSystem depending on processing method type
        :param vps_type:str type of Video Processing System valid types ['selfie','motion']
        :return: object of ProcessingSystem
        """
        if vps_type == 'selfie':
            print('Initializing Selfie Segmentation Based CAE...')
            return SelfieSegmetationBasedCAE()
        '''
        if vps_type == 'motion':
            print('Initializing Motion Based CAE...')
            return PsdEstimationBasedAudioDenoiser()
        '''
        print('[Error] Not Supported VPS....')
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
            print('Video Processing Mode...')
            # create the vps using __get_vps()
            processing_system = self.__get_vps(request.aps_type)
            # set requests video config in the created vps
            # chunk_size is equal to size of image * 3 is number of channels
            chunk_size = request.video_config.width * request.video_config.height * 3
        # check if audio config in the request in not none then create and aps using __get_aps()
        elif request.audio_config:
            print('Audio Processing Mode...')
            # create the aps using __get_aps()
            processing_system = self.__get_aps(request.aps_type)
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
            print('[Error] Not Detected Config.....')
            exit(-1)
        # return the result
        return processing_system, chunk_size

    def __select_url(self, urls):
        # Should select h264 only for video or same as codec
        return urls[0]

    def serve_request(self, request):
        # 1. Create (APS or VPS) Depending on Request
        processing_system, chunk_size = self.__get_processing_system(request)

        # 2. Create Receiver using Receiver Factory Depending on Request URL
        receiver = StreamyManger.receiver_factory.get_receiver(url=request.stream_url)
        receiver.set_config(request=request)

        # 3. Create Sender using Sender Factory Depending on Request URL
        sender = StreamyManger.sender_factory.get_sender(url=request.rtmp_server_url)
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
        # if Audio Config is detected in the received request then create a decode and encode audio processes
        if request.audio_config:
            # create the decoding audio process
            decoding_process = decode_audio(audio_src=audio_src, audio_config=request.audio_config)
            # create the encoding audio process
            encoding_process = encode_audio(video_src=video_src, audio_config=request.audio_config, dst=destination_url)
        # else if Audio Config is detected in the received request then create a decode and encode audio processes
        elif request.video_config:
            # create the decoding video process
            decoding_process = decode_video(video_src=video_src, video_config=request.video_config)
            # create the decoding audio process
            encoding_process = encode_video(audio_src=audio_src, video_config=request.video_config, dst=destination_url)
        # attach process to sender and receiver!!!!!!!!!!!!!!!!
        # untreated raw data is the decoding process stdout
        untreated_raw_data_stdout = decoding_process.stdout
        treated_raw_data_stdin = encoding_process.stdin
        while True:
            # read data from the receiver
            untreated_data_chunk = untreated_raw_data_stdout.read(chunk_size)
            #cv2.imshow('hello', np.frombuffer(untreated_data_chunk,dtype=np.uint8).reshape(480,854,3))
            #if cv2.waitKey(1) & 0xFF == 27:
            #    exit()
            if untreated_data_chunk:
                # process data using processing system
                treated_data_chunk = processing_system.process(untreated_data_chunk)
                # write processed data to the sender
                treated_raw_data_stdin.write(treated_data_chunk)