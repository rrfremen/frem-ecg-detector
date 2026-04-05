# internal
from collections import deque
from multiprocessing import shared_memory

# external
import numpy as np
from scipy.signal import butter, sosfiltfilt
import wfdb


class ProcessingPipeline:
    def __init__(self, config:dict):
        self.config_global = config
        self.config_local = {}

        # detection variables
        self.threshold_reached = False
        self.detector_window = 0.8  # percentage of latency window
        detector_window_sample = int(self.ms_to_fs(self.config_global['preprocessing']['processing_stability_latency']) * self.detector_window)
        self.detector_holder = deque([0] * detector_window_sample, maxlen=detector_window_sample)
        self.detector_index = 0
        self.beat_idx_from_latest = 0
        self.detector_freeze = False

        # Adaptive Integrating Threshold
        self.ait_init = True
        self.ait_value = 0

        # adaptive steep slope threshold
        self.asst = deque([0.0] * 5, maxlen=5)
        self.asst_ratio = 0.6
        self.asst_value = 0
        self.asst_current_peak = 0

    def ms_to_fs(self, x):
        return int(x * self.config_global['recordings']['fs'] / 1000)

    def extract_recording(self):
        pass

    def signal_preprocessing(self, signal):
        # assign parameters
        low_pass, high_pass = self.config_global['preprocessing']['bandpass_low'], self.config_global['preprocessing']['bandpass_high']
        moving_avg_window = self.config_global['preprocessing']['avg_window']
        # digital butter filter
        sos = butter(N=4,
                     Wn=[low_pass, high_pass],
                     btype='bandpass',
                     fs=self.config_global['recordings']['fs'],
                     output='sos')
        res = sosfiltfilt(sos, signal)
        res = np.gradient(res)
        res = np.square(res)
        res = np.convolve(res, np.ones(moving_avg_window)/moving_avg_window, mode='same')
        return res

    def signal_detector(self, last_det, signal_processed):
        latest_signal = signal_processed[-1]
        det = 0

        def calculate_det_threshold(sig):
            relevant_sig = sig[-self.ms_to_fs(350):]
            if self.ait_init:
                ait = np.mean(relevant_sig)
                self.ait_init = False
            else:
                ait_first = np.mean(relevant_sig[:self.ms_to_fs(50)])
                ait_last = np.mean(relevant_sig[-self.ms_to_fs(50):])
                ait = ait_first - ait_last
                # ait = 0
            if self.asst_value != 0:
                if self.asst_current_peak > self.asst_current_peak * 0.6:
                    self.asst_value -= (self.asst_current_peak - self.asst_current_peak * 0.6) / 360
            return ait + self.asst_value

        if not self.threshold_reached and not self.detector_freeze:
            det = calculate_det_threshold(signal_processed)

        if latest_signal > det and not self.threshold_reached and not self.detector_freeze:
            self.threshold_reached = True

        if self.threshold_reached and not self.detector_freeze:
            det = last_det
            self.detector_holder.append(latest_signal)
            self.detector_index += 1
            if self.detector_index >= len(self.detector_holder):
                beat_idx, beat_val = max(enumerate(self.detector_holder), key=lambda x: x[1])
                self.beat_idx_from_latest = len(self.detector_holder) - beat_idx

                self.asst.append(beat_val * self.asst_ratio)
                self.asst_value = np.mean(self.asst)
                self.asst_current_peak = np.mean(self.asst)

                self.detector_freeze = True
                self.detector_index = 0
                self.threshold_reached = False
        elif not self.threshold_reached and self.detector_freeze:
            det = last_det
            self.beat_idx_from_latest += 1
            if self.beat_idx_from_latest > self.ms_to_fs(200):
                self.detector_freeze = False
                self.beat_idx_from_latest = 0

        return det

    def run(self, pipe_processing):
        process_running, process_paused = True, False
        print('starting processing pipeline')

        # offline dataset
        current_recording = wfdb.rdrecord(self.config_global['recordings']['paths'][0])
        if self.config_global['recordings']['channels_in_use'][0] not in current_recording.sig_name:  # [0] is temporary
            raise ValueError('Selected channels not found in recording')
        fs = self.config_global['recordings']['fs']

        # windows and indexes
        sample_index = 0
        processing_latency = self.ms_to_fs(self.config_global['preprocessing']['processing_stability_latency'])  # introduce latency for processing
        processing_window = fs + processing_latency
        batch_index, batch_window = 0, int(fs/self.config_global['preprocessing']['batch_window'])  # 20 ms batch

        # data holder
        raw_signal = current_recording.p_signal[:, 0]
        index_dq = deque([0] * processing_window, maxlen=processing_window)
        index_delayed_dq = deque([0] * fs, maxlen=fs)
        signal_dq = deque([0] * processing_window, maxlen=processing_window)
        signal_delayed_dq = deque([0] * fs, maxlen=fs)
        signal_processed_dq = deque([0] * fs, maxlen=fs)
        detector_dq = deque([0] * fs, maxlen=fs)
        result_holder = np.zeros(self.config_global['preprocessing']['shm']['shape'])

        # shared memory assignments
        shm_raw = shared_memory.SharedMemory(name=self.config_global['preprocessing']['shm']['name'], create=False)
        shm_ver = np.ndarray(shape=(1,), dtype=np.uint64, buffer=shm_raw.buf, offset=0)
        shm_arr = np.ndarray(
            shape=self.config_global['preprocessing']['shm']['shape'],
            dtype=np.float64,
            buffer=shm_raw.buf,
            offset=self.config_global['preprocessing']['shm']['version_bytes']
        )
        shm_ver[0] = 0  # initialize version
        pipe_processing.send('shm_attached')  # send handshake confirmation
        print('sent handshake to main process')

        while process_running:
            # check for any command from GUI
            if pipe_processing.poll() and not process_paused:
                signal_from_gui = pipe_processing.recv()
                if type(signal_from_gui) == str:
                    if signal_from_gui == 'Pause':
                        process_paused = True
                    elif signal_from_gui == 'Stop':
                        break
            elif process_paused:  # block the loop if paused
                signal_from_gui = pipe_processing.recv()
                if type(signal_from_gui) == str:
                    if signal_from_gui == 'Continue':
                        process_paused = False
                    elif signal_from_gui == 'Stop':
                        break

            # pass on sample index and ecg sample to their ring buffer
            index_dq.append(sample_index)
            signal_dq.append(raw_signal[sample_index])

            # pre-processing stuff
            signal = np.asarray(signal_dq)
            signal_processed = self.signal_preprocessing(signal)

            signal_delayed_dq.append(signal[-processing_latency-1])
            index_delayed_dq.append(index_dq[-processing_latency-1])
            signal_processed_dq.append(signal_processed[-processing_latency-1])

            # detector - only activates after a full fs length to ensure window availability
            if sample_index > fs:
                det = self.signal_detector(detector_dq[-1], np.asarray(signal_processed_dq))
                detector_dq.append(det)

            # result
            if sample_index < processing_window:
                sample_index += 1
                continue

            if batch_index >= batch_window:
                # TODO - eventually send non-delayed raw signal
                shm_ver[0] += 1  # odd number - writing
                # ecg data here
                result_holder[:, 0] = np.asarray(index_delayed_dq)
                result_holder[:, 1] = np.asarray(signal_delayed_dq)
                result_holder[:, 2] = np.asarray(signal_processed_dq)
                result_holder[:, 3] = np.asarray(detector_dq)
                shm_arr[:] = result_holder
                shm_ver[0] += 1  # even number - version is stable

                pipe_processing.send('data_available')
                batch_index = 0

            batch_index += 1
            sample_index += 1
