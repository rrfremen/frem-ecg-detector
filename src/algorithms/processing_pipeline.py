# internal
from collections import deque

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
        result = {}

        # offline dataset
        current_recording = wfdb.rdrecord(self.config_global['recordings']['paths'][0])
        if self.config_global['recordings']['channels_in_use'][0] not in current_recording.sig_name:  # [0] is temporary
            raise ValueError('Selected channels not found in recording')

        value_index = 0
        processing_window = self.config_global['recordings']['fs']

        # temporary
        # signal = np.zeros((1, processing_window))
        # detector = np.zeros((1, processing_window))
        raw_signal = current_recording.p_signal[:, 0]
        signal_dq, detector_dq = deque(maxlen=processing_window), deque(maxlen=processing_window)

        while process_running:
            # wait for command
            # signal_from_gui = pipe_processing.poll()  # non-blocking
            # if signal_from_gui:  # process command
            #     pass

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

            # result
            result.update({

            })

            # pipe_processing.send(result)
            value_index += 1
