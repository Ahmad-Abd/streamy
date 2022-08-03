import numpy as np
from scipy.special import jv
from scipy import signal
import scipy
from scipy.io import wavfile
import matplotlib.pyplot as plt
import os


# from ProcessingSystems.ProcessingSystem import ProcessingSystem
class ThresholdBasedAudioDenoiser():
    def __init__(self,
                 threshold=20,
                 fuzziness=0.03,
                 alpha=0.1,
                 fs=44100,
                 block_size=2048,
                 sample_type=np.int16,
                 channels=1):
        self.threshold = threshold + 0.0001
        self.fuzziness = fuzziness
        self.fuzzy_gauss_sigma = self.fuzziness * self.threshold
        self.alpha = alpha
        self.fs = fs
        self.block_size = block_size
        self.sample_type = sample_type
        self.channels = channels
        self.buffer = np.zeros(block_size // 2, dtype=np.int16)
        self.old_overlap_chunk = np.zeros(block_size // 2, dtype=np.int16).tolist()
        self.old_r = np.zeros(block_size // 2 + 1, dtype=np.int16)
        self.frames = []

    def fuzzy_thresholding(self, data):
        def gaussian(x, mu, sig):
            return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)) + 0.000001)
        thresholded_data = data.copy()
        mask = thresholded_data <= self.threshold
        masked_diff = thresholded_data[mask] - self.threshold
        thresholded_data[mask] = thresholded_data[mask] * gaussian(masked_diff, 0, self.fuzzy_gauss_sigma)
        return thresholded_data

    def convert_to_exp_form(self, data):
        return np.abs(data), np.angle(data)

    def convert_to_normal_from(self, r, theta):
        return r * np.exp(1j * theta)

    def process(self, block):
        # for more than one channel use numpy.apply_along_axis or take mean on axis 1
        # convert the bytes block to numpy array
        block = np.frombuffer(block, dtype=np.int16)
        self.old_overlap_chunk.extend(block.tolist()[:(self.block_size // 2)])
        self.frames.append(self.old_overlap_chunk.copy())
        self.frames.append(block.tolist())
        self.old_overlap_chunk = block.tolist()[(self.block_size // 2):].copy()
        results = []
        for frame in self.frames:
            # compute STFT
            f, t, Zxx = signal.stft(frame, self.fs, nperseg=self.block_size)
            # thresholding
            Zxx[:, 0] = 0
            r, theta = self.convert_to_exp_form(Zxx[:, 1])
            new_r = self.fuzzy_thresholding(r)
            new_r = (1 - self.alpha) * new_r + (self.alpha) * self.old_r
            self.old_r = new_r.copy()
            Zxx[:, 1] = self.convert_to_normal_from(new_r, theta)
            Zxx[:, 2] = 0
            # compute ISTFT
            _, reconstructed = signal.istft(Zxx, self.fs, nperseg=self.block_size)
            reconstructed = reconstructed.reshape(-1).astype(np.int16)
            # OLA & Re-buffering
            reconstructed[:self.block_size // 2] = reconstructed[:self.block_size // 2] + self.buffer
            results.extend(reconstructed[:(self.block_size // 2)].copy().tolist())
            self.buffer = reconstructed[(self.block_size // 2):].copy()
        processed_block = np.array(results, dtype=np.int16).tobytes()
        self.frames = []
        # return the result
        return processed_block

    def late_processing(self, data, sr):
        i = 0
        processed_data = []
        end = (data.shape[0] // self.block_size)
        while i != end:
            block = data[i * self.block_size:(i + 1) * self.block_size]
            block = block.tobytes()
            result = self.process(block)
            processed_data.extend(np.frombuffer(result, dtype=np.int16).tolist())
            i += 1
        return processed_data

