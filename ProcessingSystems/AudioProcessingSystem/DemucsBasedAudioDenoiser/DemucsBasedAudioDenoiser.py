#from ProcessingSystems.ProcessingSystem import ProcessingSystem
import torch
import torchaudio
import os
from ProcessingSystems.AudioProcessingSystem.DemucsBasedAudioDenoiser.denoiser import pretrained
from ProcessingSystems.AudioProcessingSystem.DemucsBasedAudioDenoiser.denoiser.demucs import DemucsStreamer
from ProcessingSystems.AudioProcessingSystem.DemucsBasedAudioDenoiser.denoiser.dsp import convert_audio
from scipy.io import wavfile
import numpy as np
from IPython import display as disp
import time
import os
import matplotlib.pyplot as plt
import numpy as np
from scipy.special import jv
from scipy import signal
import scipy
class DemucsBasedAudioDenoiser():
    def __init__(self,
                 threshold=0,
                 fs=16000,
                 block_size=512,
                 sample_type=np.int16,
                 channels=1):
        self.threshold = threshold
        self.fs = fs
        self.block_size = block_size
        self.sample_type = sample_type
        self.channels = channels
        self.buffer = np.zeros(block_size//2, dtype=np.int16)
        self.old_overlap_chunk = np.zeros(
            block_size//2, dtype=np.int16).tolist()
        self.old_r = np.zeros(block_size // 2 + 1, dtype=np.int16)
        self.alpha = 0.1
        self.dry = 0
        self.num_frames = 5
        self.first = True
        self.current_time = 0
        self.last_log_time = 0
        self.last_error_time = 0
        self.cooldown_time = 2
        self.log_delta = 10
        self.model = pretrained.dns48().cpu()
        self.model.eval()
        self.streamer = DemucsStreamer(self.model, dry=self.dry, num_frames=self.num_frames)
        self.sr_ms = self.model.sample_rate / 1000
        self.stride_ms = self.streamer.stride / self.sr_ms
        self.pcm2float_i = np.iinfo(sample_type)
        self.pcm2float_abs_max = 2 ** (self.pcm2float_i.bits - 1)
        self.pcm2float_offset = self.pcm2float_i.min + self.pcm2float_abs_max
        self.float2pcm_i = np.iinfo(sample_type)
        self.float2pcm_abs_max = 2 ** (self.float2pcm_i.bits - 1)
        self.float2pcm_offset = self.float2pcm_i.min + self.float2pcm_abs_max

    def pcm2float(self,sig, dtype='float32'):
        return (sig.astype(dtype) - self.pcm2float_offset) / self.pcm2float_abs_max

    def float2pcm(self,sig, dtype='int16'):
        return (sig * self.float2pcm_abs_max + self.float2pcm_offset).clip(self.float2pcm_i.min, self.float2pcm_i.max).astype(dtype)

    def process(self, block):
        # for more than one channel use numpy.apply_along_axis or take mean on axis 1
        block = np.frombuffer(block, dtype=self.sample_type)
        block = self.pcm2float(block)
        length = self.streamer.total_length if self.first else self.streamer.stride
        self.first = False
        self.current_time += length / self.model.sample_rate
        frame = torch.tensor(block).to('cpu')
        with torch.no_grad():
            out = self.streamer.feed(frame[None])[0]
        out.clamp_(-1, 1)
        out = out.cpu().numpy().astype(np.float32).reshape(-1)
        out = self.float2pcm(out)
        processed_block = out.astype(self.sample_type).tobytes()
        return processed_block
    
    def late_processing(self,data ,sr):
        i = 0
        processed_data = []
        end = data.shape[0] // self.block_size
        while i != end:
            block = data[i * self.block_size:(i + 1) * self.block_size]
            block = block.tobytes()
            result = self.process(block)
            processed_data.extend(np.frombuffer(result,dtype = np.int16).tolist())
            i += 1
        return processed_data




