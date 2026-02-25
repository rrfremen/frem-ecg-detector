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
        process_running, process_paused = True, False
        print('starting processing pipeline')

        def ms_to_fs(x):
            return int(x*self.config_global['recordings']['fs']/1000)

        # offline dataset
        current_recording = wfdb.rdrecord(self.config_global['recordings']['paths'][0])
        if self.config_global['recordings']['channels_in_use'][0] not in current_recording.sig_name:  # [0] is temporary
            raise ValueError('Selected channels not found in recording')

        sample_index = 0
        processing_window = self.config_global['recordings']['fs']

        # data holder
        raw_signal = current_recording.p_signal[:, 0]
        index_dq = deque([0] * processing_window, maxlen=processing_window)
        signal_dq = deque([0] * processing_window, maxlen=processing_window)
        detector_dq = deque([0] * processing_window, maxlen=processing_window)
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
                    if signal_from_gui == 'paused':
                        process_paused = True
            elif process_paused:  # block the loop if paused
                signal_from_gui = pipe_processing.recv()
                if type(signal_from_gui) == str:
                    if signal_from_gui == 'continue':
                        process_paused = False
                    elif signal_from_gui == 'stop':
                        process_running = False

            # pass on sample index and ecg sample to their ring buffer
            index_dq.append(sample_index)
            signal_dq.append(raw_signal[sample_index])

            # pre-processing stuff
            signal = np.asarray(signal_dq)
            sos = butter(N=4,
                         Wn=[self.config_global['preprocessing']['bandpass_low'], self.config_global['preprocessing']['bandpass_high']],
                         btype='bandpass',
                         fs=self.config_global['recordings']['fs'],
                         output='sos')
            signal_processed = sosfiltfilt(sos, signal)

            # detector
            if sample_index < (1000 * self.config_global['recordings']['fs'] * 350):
                detector = 0
            else:  # threshold for AIT surpassed
                detector = np.mean(signal_processed[-ms_to_fs(350):])

            # pass on detector sample to its ring buffer
            detector_dq.append(detector)

            write_result = True
            # result
            if write_result:
                shm_ver[0] += 1  # odd number - writing
                # ecg data here
                result_holder[:, 0] = np.asarray(index_dq)
                result_holder[:, 1] = signal
                result_holder[:, 2] = signal_processed
                result_holder[:, 3] = np.asarray(detector_dq)
                shm_arr[:] = result_holder
                shm_ver[0] += 1  # even number - version is stable

                pipe_processing.send('data_available')

            sample_index += 1
