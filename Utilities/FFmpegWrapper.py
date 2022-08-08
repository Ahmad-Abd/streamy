# 1. detect hardware (nvediea or AMD) or copy same
'''
Encode AVI to h.265 Video (Software Encoding)

ffmpeg -i input.avi -c:v libx265 output.mp4

Encode AVI to h.264 Video (AMD GPU Encoding)

ffmpeg -i input.avi -c:v h264_amf output.mp4

Encode AVI to h.265 Video (AMD GPU Encoding)

ffmpeg -i input.avi -c:v hevc_amf output.mp4

Encode AVI to h.264 Video (NVIDIA GPU Encoding)

ffmpeg -i input.avi -c:v h264_nvenc output.mp4

Encode AVI to h.265 Video (NVIDIA GPU Encoding)

ffmpeg -i input.avi -c:v hevc_nvenc output.mp4

secure or not
sample_fmts pix_fmt
block video or audio
bitrate_limit and p_strategy in H264 option
-preset type
Configuration preset. This does some automatic settings based on the general type of the image.

none
Do not use a preset.

default
Use the encoder default.

picture
Digital picture, like portrait, inner shot

photo
Outdoor photograph, with natural lighting

drawing
Hand or line drawing, with high-contrast details

icon
Small-sized colorful images

text
Text-like

fftdnoiz
# https://trac.ffmpeg.org/wiki/Encode/H.264 see max_rate
'''
import subprocess


def decode_audio(audio_src, dst_audio_config, src_audio_config):
    print('audio decode\n\n\n')
    audio_decoding_process = subprocess.Popen(['ffmpeg',
                                               '-thread_queue_size', '1000000',
                                               '-i', audio_src,
                                               '-ac', str(dst_audio_config.channels),
                                               '-ar', str(dst_audio_config.sample_rate),
                                               '-f', 's16le',
                                               'pipe:1'], stdout=subprocess.PIPE)
    return audio_decoding_process


def decode_video(video_src, dst_video_config, src_video_config):
    print('video decode\n\n\n\n\n')
    video_decoding_process = subprocess.Popen(['ffmpeg',
                                               # '-loglevel', 'quiet',
                                               '-thread_queue_size', '1000000',
                                               '-i', video_src,
                                               '-f', 'rawvideo',
                                               '-pix_fmt', 'bgr24',
                                               'pipe:1'], stdout=subprocess.PIPE)
    return video_decoding_process


def encode_video(audio_src, dst_video_config, src_video_config, dst):
    print('video encode\n\n\n\n\n')
    # encoding process with aggregator
    encoding_process = subprocess.Popen(['ffmpeg',
                                         '-re',
                                         '-i', audio_src,
                                         '-f', 'rawvideo',
                                         '-s', f'{dst_video_config.width}x{dst_video_config.height}',
                                         '-r', str(src_video_config.fps),
                                         '-pix_fmt', 'bgr24',
                                         '-thread_queue_size', '10000',
                                         '-i', 'pipe:0',
                                         '-c:v', 'libx264',
                                         '-c:a', 'copy',
                                         '-color_primaries', 'bt709',
                                         '-profile:v', 'main',
                                         '-pix_fmt', 'yuv420p',
                                         '-crf', '25',
                                         '-preset', 'veryfast',
                                         '-g', str(2*src_video_config.fps),
                                         '-f', 'flv',
                                         dst], stdin=subprocess.PIPE)
    '''
    encoding_process = subprocess.Popen(['ffmpeg',
                                         '-re',
                                         '-hwaccel', 'cuda',
                                         '-hwaccel_output_format', 'cuda',
                                         '-thread_queue_size', '8',
                                         '-f', 'rawvideo',
                                         '-s', '640x360',
                                         '-i', 'pipe:0',
                                         '-i', audio_src,
                                         '-f', 'flv',
                                         '-c:a', 'copy',
                                         '-c:v', 'h264_nvenc',
                                         '-s', '640x360',
                                         '-profile:v', 'baseline',
                                         '-pix_fmt', 'yuv420p',
                                         '-preset', 'fast',
                                         '-tune', 'zerolatency',
                                         '-crf', '28',
                                         '-g', '40',
                                         dst], stdin=subprocess.PIPE)
        '''
    return encoding_process


def encode_audio(video_src, dst_audio_config, src_audio_config, dst):
    print('audio encode\n\n\n\n\n')
    # encoding process with aggregator
    encoding_process = subprocess.Popen(['ffmpeg',
                                         '-re',
                                         '-i', video_src,
                                         '-f', 's16le',
                                         '-ac', str(dst_audio_config.channels),
                                         '-ar', str(dst_audio_config.sample_rate),
                                         '-thread_queue_size', '1000000',
                                         '-i', 'pipe:0',
                                         '-f', 'flv',
                                         '-c:a', 'aac',
                                         '-c:v', 'copy',
                                         '-q:a', '1',
                                         '-aac_coder', 'fast',
                                         dst], stdin=subprocess.PIPE)
    return encoding_process
