from Messages.AudioConfig import AudioConfig
from Messages.StreamyFormRequest import StreamyFormRequest
from Messages.VideoConfig import VideoConfig
from ProcessingSystems.AudioProcessingSystem.ThresholdingBasedAudioDenoiser.ThresholdBasedAudioDenoiser import ThresholdBasedAudioDenoiser
from Receiver.ReceiverFactory import ReceiverFactory
from Manger.Manger import Manger
from Sender.SenderFactory import SenderFactory
from Utilities.FFmpegWrapper import *


class StreamyManger(Manger):
    receiver_factory = ReceiverFactory()
    sender_factory = SenderFactory()

    def __get_processing_system(self, request):
        processing_system, chunk_size = None, None
        if request.video_config:
            chunk_size = request.video_config.width * request.video_config.height * 3
        elif request.audio_config:
            processing_system = ThresholdBasedAudioDenoiser()
            chunk_size = request.audio_config.sample_rate * request.audio_config.channels
        else:
            print('No Detected Config.....')
            exit(-1)
        return processing_system, chunk_size

    def __select_url(self, urls):
        # Should select h264 only for video or same as codec
        return urls[0]

    def serve_request(self, request):
        # 1. Create (APS or VPS or TPS) Depending on Request
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
            # get audio and video src from the receiver
            audio_src, video_src = receiver.receive(url=request.stream_url)
            # get the destination url from the sender
            destination_url = sender.send()
            # test
            print(destination_url)
        except Exception as e:
            print(e)
            exit(-1)
        decoding_process = None
        encoding_process = None
        if request.audio_config:
            decoding_process = decode_audio(audio_src=audio_src, audio_config=request.audio_config)
            encoding_process = encode_audio(video_src=video_src, audio_config=request.audio_config, dst=destination_url)
        elif request.video_config:
            decoding_process = decode_video(video_src=video_src, video_config=request.video_config)
            encoding_process = encode_video(audio_src=audio_src, video_config=request.video_config, dst=destination_url)
        # attach process to sender and receiver!!!!!!!!!!!!!!!!
        untreated_raw_data_stdout = decoding_process.stdout
        treated_raw_data_stdin = encoding_process.stdin
        while True:
            # read data from the receiver
            untreated_data_chunk = untreated_raw_data_stdout.read(chunk_size)
            # process data using processing system
            treated_data_chunk = processing_system.process(untreated_data_chunk)
            # write processed data to the sender
            treated_raw_data_stdin.write(treated_data_chunk)
