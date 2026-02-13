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

    def extract_recording(self):
        pass

    def run(self, pipe_processing):
        process_running = True

        # offline dataset
        current_recording = wfdb.rdrecord(self.config_global['recordings']['paths'][0])
        if self.config_global['recordings']['channels_in_use'][0] not in current_recording.sig_name:  # [0] is temporary
            raise ValueError('Selected channels not found in recording')

        value_index = 0
        processing_window = self.config_global['recordings']['fs']

        # data holder
        raw_signal = current_recording.p_signal[:, 0]
        signal_dq, detector_dq = deque(maxlen=processing_window), deque(maxlen=processing_window)

        # shared memory assignments
        shm_raw = shared_memory.SharedMemory(name=self.config_global['preprocessing']['shm']['name'], create=False)
        shm_ver = np.ndarray(shape=(1,), dtype=np.uint64, buffer=shm_raw.buf, offset=0)
        shm_arr = np.ndarray(
            shape=self.config_global['preprocessing']['shm']['shape'],
            dtype=np.float64,
            buffer=shm_raw.buf,
            offset=self.config_global['processing']['shm']['version_bytes']
        )
        shm_ver[0] = 0  # initialize version
        pipe_processing.send('shm_attached')  # send handshake confirmation

        while process_running:
            # check for any command from GUI
            if pipe_processing.poll(timeout=1/self.config_global['recordings']['fs']):
                signal_from_gui = pipe_processing.recv()

            # pass on sample
            signal_dq.append(raw_signal[value_index])

            # pre-processing stuff
            signal = np.asarray(signal_dq)
            sos = butter(N=4,
                         Wn=[self.config_global['preprocessing']['bandpass_low'], self.config_global['preprocessing']['bandpass_high']],
                         btype='bandpass',
                         fs=self.config_global['recordings']['fs'],
                         output='sos')
            signal_processed = sosfiltfilt(sos, signal)

            # detector
            if value_index < (1000 * self.config_global['recordings']['fs'] * 350):
                detector_dq.append(0)
            else:  # threshold for AIT surpassed
                detector = np.mean(signal_processed[-350:])

            write_result = True
            # result
            if write_result:
                shm_ver[0] += 1  # odd number - writing
                # ecg data here
                shm_ver[0] += 1  # even number - version is stable

                pipe_processing.send('data_available')

            value_index += 1
