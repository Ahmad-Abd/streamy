import numpy as np
from scipy.special import jv
from scipy import signal
import scipy

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
        self.buffer = np.zeros(block_size//2 ,dtype=np.int16)
        self.old_overlap_chunk =  np.zeros(block_size//2 ,dtype=np.int16).tolist()
        self.old_r = np.zeros(block_size// 2 +1 ,dtype=np.int16)
        self.alpha = 0.1
    def fuzzy_thresholding(self ,data ,threshold, fuzeness=10):
        # fuzeness > 0
        def gaussian(x, mu, sig):
            return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))

        sigma = fuzeness * np.log10(threshold)
        # threshold/fuzeness
        thresholded_data = data.copy()
        mask = thresholded_data <= threshold
        thresholded_data[mask] = thresholded_data[mask] * gaussian(thresholded_data[mask] - threshold, 0, sigma)
        return thresholded_data

    def convert_to_exp_form(self, data):
        return np.abs(data), np.angle(data)

    def convert_to_normal_from(self, r, theta):
        return r * np.exp(1j * theta)

    def process(self, block):
        self.old_overlap_chunk.extend(block.tolist())
        block = np.array(self.old_overlap_chunk[:self.block_size]).astype(np.int16)
        del self.old_overlap_chunk[:self.block_size//2]
        # compute STFT
        f, t, Zxx = signal.stft(block, self.fs, nperseg=self.block_size)
        # thresholding
        Zxx[:, 0] = 0
        r, theta = self.convert_to_exp_form(Zxx[:, 1])
        new_r = self.fuzzy_thresholding(r, threshold=30, fuzeness=.3)
        new_r = (1 - self.alpha) * new_r + (self.alpha) * self.old_r
        self.old_r = new_r.copy()
        Zxx[:, 1] = self.convert_to_normal_from(new_r, theta)
        # Zxx[np.abs(Zxx[:,1])<20,1] = 0
        Zxx[:, 2] = 0
        # compute ISTFT
        _, reconstructed = signal.istft(Zxx, self.fs, nperseg=self.block_size)
        reconstructed = reconstructed.astype(np.int16)
        # get result
        result = reconstructed[:self.block_size // 2] + self.buffer
        # stream.write(result.astype(np.int16).tobytes())
        # re-buffering
        self.buffer = reconstructed[self.block_size // 2:].copy()
        processed_block = result.astype(self.sample_type).tobytes()
        # return the result
        return processed_block