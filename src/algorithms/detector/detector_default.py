# built-in
from enum import Enum
from collections import deque

# external
import numpy as np

# internal
from .detector_base import BaseDetector
from ..math_utils import ms_to_fs


class DetectorState(Enum):
    FREEZE = 'freeze'
    DETECTING = 'detecting'
    SEARCHING_PEAK = 'searching_peak'


class DefaultDetector(BaseDetector):
    def __init__(self):
        super().__init__()

        self.state = ''
        self.fs = 0

        self.detector_window = 0
        self.detector_holder = None
        self.detector_holder_prev = []
        self.detector_index = 0
        self.beat_idx_from_latest = 0

        # Adaptive Integrating Threshold
        self.ait_active = True
        self.ait_init = True

        # Adaptive Steep Slope Threshold
        self.asst_active = True
        self.asst = deque([0.0] * 5, maxlen=5)
        self.asst_ratio = 0.6
        self.asst_current_value = 0
        self.asst_current_peak = 0

    def set_config(self, config: dict):
        self.fs = config.get('recordings', {}).get('fs', 1)
        self.detector_window = config.get('detector', {}).get('params', {}).get('detector_window', 20)
        self.ait_active = config.get('detector', {}).get('params', {}).get('ait_active', True)
        self.asst_active = config.get('detector', {}).get('params', {}).get('asst_active', True)
        self.asst_ratio = config.get('detector', {}).get('params', {}).get('asst_ratio', 0.6)

        self.detector_holder = deque([0] * self.detector_window, maxlen=self.detector_window)
        self.state = DetectorState.DETECTING

    def update_config(self, key: str, value):
        pass

    def detect(self, last_det, signal) -> tuple[float, int]:
        latest_signal = signal[-1]
        det = 0
        beat_loc = 0

        if self.state == DetectorState.DETECTING:
            det = self.calculate_detector(signal)

        if latest_signal > det and self.state == DetectorState.DETECTING:
            self.state = DetectorState.SEARCHING_PEAK

        if self.state == DetectorState.SEARCHING_PEAK:
            det = last_det
            self.detector_holder.append(latest_signal)
            self.detector_index += 1
            if self.detector_index >= len(self.detector_holder):
                if not self.detector_holder_prev:
                    self.detector_holder_prev = self.detector_holder.copy()
                else:
                    mean_prev = np.mean(self.detector_holder_prev)
                    mean_new = np.mean(self.detector_holder)
                    if mean_new <= mean_prev:
                        beat_idx, beat_val = max(enumerate(self.detector_holder_prev), key=lambda x: x[1])
                        self.beat_idx_from_latest = len(self.detector_holder_prev) * 2 - beat_idx
                        beat_loc = -self.beat_idx_from_latest

                        if self.asst_active:
                            self.asst.append(beat_val * self.asst_ratio)
                            self.asst_current_value = np.mean(self.asst)
                            self.asst_current_peak = np.mean(self.asst)

                        self.detector_holder_prev = []
                        self.state = DetectorState.FREEZE
                    else:
                        self.detector_holder_prev = self.detector_holder.copy()
                self.detector_index = 0
        if self.state == DetectorState.FREEZE:
            det = last_det
            self.beat_idx_from_latest += 1
            if self.beat_idx_from_latest > ms_to_fs(self.fs, 200):
                self.state = DetectorState.DETECTING
                self.beat_idx_from_latest = 0

        return det, beat_loc

    def calculate_detector(self, sig):
        ait, asst = 0, 0
        if self.ait_active:
            relevant_sig = sig[-ms_to_fs(self.fs, 350):]
            if self.ait_init:
                ait = np.mean(relevant_sig)
                self.ait_init = False
            else:
                ait_first = np.mean(relevant_sig[:ms_to_fs(self.fs, 50)])
                ait_last = np.mean(relevant_sig[-ms_to_fs(self.fs, 50):])
                ait = ait_first-ait_last

        if self.asst_active:
            if self.asst_current_value != 0:
                if self.asst_current_value > self.asst_current_peak * 0.6:
                    self.asst_current_value -= self.asst_current_value * 0.4 / self.fs
            asst = self.asst_current_value

        return ait + asst
