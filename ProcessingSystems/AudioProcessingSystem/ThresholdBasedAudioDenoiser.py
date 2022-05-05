import numpy as np
from scipy import signal
from ProcessingSystems.ProcessingSystem import ProcessingSystem


class ThresholdBasedAudioDenoiser(ProcessingSystem):
    def __init__(self,
                 fs=44100,
                 block_size=2048,
                 threshold=20,
                 sample_type=np.int16,
                 channels=1):
        self.fs = fs
        self.block_size = block_size
        self.threshold = threshold
        self.sample_type = sample_type
        self.channels = channels

    def process(self, block):
        # for more than one channel use numpy.apply_along_axis
        # convert the bytes block to numpy array
        data = np.frombuffer(block, dtype=self.sample_type)
        # compute STFT to the block
        f, t, Zxx = signal.stft(data, fs=self.fs, nperseg=self.block_size)
        # threshold the STFT magnitude
        Zxx[np.abs(Zxx) < self.threshold] = 0
        # compute the inverse STFT
        _, data = signal.istft(Zxx, fs=self.fs, nperseg=self.block_size)
        # convert the numpy array to bytes block
        processed_block = data.astype(self.sample_type).tobytes()
        # return the result
        return processed_block
