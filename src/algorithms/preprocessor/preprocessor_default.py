# built-in
from collections import deque

# external
import numpy as np
from scipy.signal import butter, sosfilt

# internal
from .preprocessor_base import BasePreprocessor


class DefaultPreprocessor(BasePreprocessor):
    def __init__(self):
        super().__init__()

        self.fs = 0
        self.low_pass, self.high_pass = 0, 0
        self.sos, self.zi = 0, 0
        self.moving_avg_window, self.ma_buffer = 0, []
        self.prev_sample = 0

    def set_config(self, config: dict):
        self.fs = config.get('recordings', {}).get('fs', 1)
        self.low_pass = config.get('preprocessor', {}).get('params', {}).get('bandpass_low', 9)
        self.high_pass = config.get('preprocessor', {}).get('params', {}).get('bandpass_high', 14)
        self.moving_avg_window = config.get('preprocessor', {}).get('params', {}).get('avg_window', 40)

        self.init_preprocessor()

    def init_preprocessor(self):
        self.sos = butter(N=4, Wn=[self.low_pass, self.high_pass], btype='bandpass', fs=self.fs, output='sos')
        self.zi = np.zeros((self.sos.shape[0], 2))

        self.ma_buffer = deque([0.0] * self.moving_avg_window, maxlen=self.moving_avg_window)

    def update_config(self, key: str, value):
        pass

    def preprocess(self, sample) -> float:
        # bandpass filter
        filtered, self.zi = sosfilt(self.sos, [sample], zi=self.zi)
        filtered = filtered[0]

        # gradient
        grad = filtered - self.prev_sample
        self.prev_sample = filtered

        # square
        squared = grad * grad

        # moving average  # TODO - optimize
        self.ma_buffer.append(squared)
        avg = sum(self.ma_buffer) / len(self.ma_buffer)

        return avg
