import numpy as np
from scipy.special import jv
from scipy import signal
import scipy
from scipy.io import wavfile
import os
import matplotlib.pyplot as plt
#from ProcessingSystems.ProcessingSystem import ProcessingSystem


class PsdEstimationBasedAudioDenoiser():
    def __init__(self,
                 fs=44100,
                 block_size=2048,
                 threshold=2,
                 sample_type=np.int16,
                 channels=1,
                 time_smoothing_constant=0.90,
                 snr_estimator_smoothing_constant=0.98):
        self.fs = fs
        self.block_size = block_size
        self.threshold = threshold
        self.sample_type = sample_type
        self.channels = channels
        self.buffer = np.zeros(block_size // 2, dtype=np.int16)
        self.old_overlap_chunk = np.zeros(block_size // 2, dtype=np.int16).tolist()
        self.old_r = np.zeros(block_size // 2 + 1, dtype=np.int16)
        self.time_smoothing_constant = time_smoothing_constant
        self.snr_estimator_smoothing_constant = snr_estimator_smoothing_constant
        self.W = np.zeros(((self.block_size // 2) + 1, 1), dtype=np.float32)
        self.W[:, 0] = np.finfo(np.float32).eps
        self.prev_squared_W = self.W[:, 0].copy().reshape(-1, 1)
        self.prev_X = self.W[:, 0].copy().reshape(-1, 1)
        self.prev_frame = self.W[:, 0].copy().reshape(-1, 1)
        self.prev_G = self.W[:, 0].copy().reshape(-1, 1)

    def compute_approx_aproiri(self, Y):
        squared_Y_magnitude = (np.abs(Y)) ** 2
        v1 = (squared_Y_magnitude / self.prev_squared_W) - 1
        approx_apriori = np.fmax(v1, 0)
        return approx_apriori

    def compute_expected_noise(self, Y, apriori_snr, c=25):
        squared_Y_magnitude = (np.abs(Y)) ** 2
        expected_noise = ((1 + apriori_snr) ** -2 + (apriori_snr / ((1 + apriori_snr) * c))) * squared_Y_magnitude
        return expected_noise

    def compute_DD_aproiri_snr_estimation(self, curr_posteriori_snr, a=0.98):
        squared_prev_X_magnitude = (np.abs(self.prev_X)) ** 2
        v1 = (squared_prev_X_magnitude / self.prev_squared_W)
        v2 = np.fmax(curr_posteriori_snr - 1, 0)
        DD_aproiri_snr_estimation = self.snr_estimator_smoothing_constant * v1 + (
                1 - self.snr_estimator_smoothing_constant) * v2
        return DD_aproiri_snr_estimation

    def compute_B_inverse(self, apriori_snr):
        eps = np.finfo(np.float32).eps
        v = 1 / (1 + apriori_snr)
        B_inverse = ((1 + apriori_snr) * scipy.special.gammainc(2, v)) + np.exp(-v)
        return B_inverse

    def compute_curr_W_squared_estimation(self, expected_noise, B):
        return expected_noise * B

    def smooth_squared_W_cross_time(self, curr_squared_W, smooth_c=0.9):
        return self.time_smoothing_constant * self.prev_squared_W + (1 - self.time_smoothing_constant) * curr_squared_W

    def bessel(v, X):
        return ((1j ** (-v)) * jv(v, 1j * X)).real

    def get_gain(self, priori_SNR, aPosterioriSNR):
        # V = priori_SNR * aPosterioriSNR / (1 + priori_SNR)
        # gain = np.sqrt((priori_SNR/(priori_SNR+1))*((V+1)/(aPosterioriSNR+0.000001)))
        # gain = (math.gamma(1.5) * np.sqrt(V)) / aPosterioriSNR * np.exp(-1 * V / 2) * ((1 + V) * bessel(0, V / 2) + V * bessel(1, V / 2))
        return priori_SNR / (1 + priori_SNR)

    def _process_block(self, Y):
        curr_frame = Y.reshape(-1, 1)

        # step 1 : Compute ˆξ(k, i) using Eq. (5)
        approx_aproiri = self.compute_approx_aproiri(Y=curr_frame)

        # setp 2 : Compute E{N2|y; ˆξ(k, i)} by substituting ˆξ(k, i) from Eq.(5) into Eq. (4).
        expected_noise = self.compute_expected_noise(curr_frame, approx_aproiri, c=35)

        # step 3 : Estimate ξ(k, i) using σ2W(k, i−1) and the DD approach [1], denoted by ˆξDD .
        smoothed_frame = (self.time_smoothing_constant) * (np.abs(curr_frame) ** 2) + (1 - self.time_smoothing_constant) * (np.abs(self.prev_frame) ** 2)
        curr_posteriori_snr = smoothed_frame / self.prev_squared_W
        DD_aproiri_snr_estimation = self.compute_DD_aproiri_snr_estimation(curr_posteriori_snr, a=0.98)

        # step 4 : Compute B(ˆξDD) using Eq. (7).
        B_inverse = self.compute_B_inverse(DD_aproiri_snr_estimation)
        B = 1 / B_inverse

        # step 5 : Compute σ2W(k, i) = E{N2|y; ˆξ(k, i)}B(ˆξDD).
        curr_W_squared_estimation = self.compute_curr_W_squared_estimation(expected_noise, B)

        # step 6 : Smooth σ2W(k, i) across time to reduce its variance
        W = self.smooth_squared_W_cross_time(curr_W_squared_estimation, smooth_c=0.9)

        # step 7 : Re-calculate the posteriori snr and the gain function
        curr_posteriori_snr = (np.abs(curr_frame) ** 2) / (W + 0.00001)
        G = self.get_gain(DD_aproiri_snr_estimation, curr_posteriori_snr)

        # step 8 : Smooth the gain function across time to reduce effect of musical noise
        G = self.time_smoothing_constant * G + (1 - self.time_smoothing_constant) * self.prev_G

        # step 9 : calc the enhanced frame using : |X| = G . |Y| . exp(j*phase_of_Y)
        x = G * np.abs(curr_frame) * np.exp(1j * np.angle(curr_frame))

        # step 10 : remove unimportant components from the enhanced frame
        x[np.abs(x) < self.threshold] = 0

        # re-buffer all important values
        self.prev_X = x.copy()
        self.prev_squared_W = W.copy()
        self.prev_frame = curr_frame.copy()
        self.prev_G = G.copy()

        # return the result
        return x

    def process(self, block):
        # for more than one channel use numpy.apply_along_axis or take mean on axis 1
        # convert the bytes block to numpy array
        block = np.frombuffer(block, dtype=self.sample_type)
        self.old_overlap_chunk.extend(block.tolist())
        block = np.array(self.old_overlap_chunk[:self.block_size]).astype(np.int16)
        del self.old_overlap_chunk[:self.block_size // 2]
        # compute STFT
        f, t, Zxx = signal.stft(block, self.fs, nperseg=self.block_size)
        # process
        Zxx[:, 0] = 0
        Zxx[:, 1] = self._process_block(Zxx[:, 1]).reshape(-1).copy()
        Zxx[:, 2] = 0
        # compute ISTFT
        _, reconstructed = signal.istft(Zxx, self.fs, nperseg=self.block_size)
        reconstructed = reconstructed.astype(np.int16)
        # get result
        result = reconstructed[:self.block_size // 2] + self.buffer
        # re-buffering
        self.buffer = reconstructed[self.block_size // 2:].copy()
        processed_block = result.astype(self.sample_type).tobytes()
        # return the result
        return processed_block
    def late_processing(self,data ,sr):
        i = 0
        processed_data = []
        end = (data.shape[0] // self.block_size)*2
        while i != end:
            block = data[i * self.block_size:(i + 1) * self.block_size]
            block = block.tobytes()
            result = self.process(block)
            processed_data.extend(np.frombuffer(result,dtype = np.int16).tolist())
            i += 1
        return processed_data

