# import the libraries
from pytube import YouTube
import time
import ffmpeg
import numpy as np
import cv2
import os
import subprocess
from pafy import pafy
from datetime import datetime
import pafy


# config
url = 'https://youtu.be/Q_HoGYhk4x8'
vPafy = pafy.new(url)
video_src = vPafy.videostreams[7].url
audio_src = vPafy.audiostreams[2].url
dst = 'rtmp://a.rtmp.youtube.com/live2/3wgb-cv03-ckyy-jmxc-cw42'


# audio decoding process
audio_decoding_process = subprocess.Popen(['ffmpeg' ,
                      '-i' ,audio_src ,
                      '-ac','1' ,
                      '-ar','44100' ,
                      '-f','s16le' ,
                      'pipe:1'],stdout=subprocess.PIPE)


# video decoding process
video_decoding_process = subprocess.Popen(['ffmpeg' ,
                      '-c:v' ,'h264_cuvid',
                      '-i' ,video_src ,
                      '-pix_fmt' ,'yuv420p',
                      '-r' ,'25',
                      '-s' ,'640x360',
                      '-f' ,'rawvideo',
                      'pipe:1'],stdout=subprocess.PIPE)


# define the multiple named pipes
raw_video_pipe = 'raw_video_pipe'
raw_audio_pipe = 'raw_audio_pipe'
try:
    os.unlink(raw_video_pipe)
    os.unlink(raw_audio_pipe)
except:
    print('pipes not exist...')
os.mkfifo(raw_video_pipe)
os.mkfifo(raw_audio_pipe)


# encoding process with aggregator
encoding_process = subprocess.Popen(['ffmpeg' ,
                                         '-re' ,
                                         '-hwaccel', 'cuda',
                                         '-hwaccel_output_format', 'cuda',
                                         '-thread_queue_size', '8',
                                         '-f' ,'rawvideo',
                                         '-s' ,'640x360',
                                         '-i' ,raw_video_pipe,
                                         '-i' ,audio_src,
                                         '-f' ,'flv' ,
                                         '-c:a' ,'copy',
                                         '-c:v' ,'h264_nvenc' ,
                                         '-s' ,'640x360',
                                         '-profile:v', 'baseline',
                                         '-pix_fmt' ,'yuv420p',
                                         '-preset', 'fast',
                                         '-tune', 'zerolatency',
                                         '-crf', '28',
                                         '-g', '40',
                                         dst],stdin=subprocess.PIPE)

# open the multiple named pipes
video_pipe = os.open(raw_video_pipe, os.O_WRONLY)
#audio_pipe = os.open(raw_audio_pipe, os.O_WRONLY)
print('\n\n\nDone Pipes Openned Successfuly\n\n')


# read from decoding and write to encoding process
while True:
  video_bytes = video_decoding_process.stdout.read(640*360*3*20)
  audio_bytes = audio_decoding_process.stdout.read(44100*2)
  if audio_bytes and video_bytes:
    os.write(video_pipe ,video_bytes)
    #os.write(audio_bytes ,audio_pipe)