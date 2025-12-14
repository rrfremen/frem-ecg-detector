import numpy as np
from scipy.signal import butter, filtfilt
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

        current_recording = wfdb.rdrecord(self.config_global['recordings']['paths'][0])
        if self.config_global['recordings']['channels_in_use'] not in current_recording.sig_name:
            raise ValueError('Selected channels not found in recording')
        original_ecg = None
        time_index = None
        preprocessing_window = 1 * self.config_global['recordings']['fs']
        preprocessing_holder = np.zeros((1, preprocessing_window))

        while process_running:
            signal_from_gui = pipe_processing.poll()  # non-blocking
            if signal_from_gui:  # process command
                pass
            # pre-processing stuff

            # detector

            # result
            result.update({

            })

            pipe_processing.send(result)
