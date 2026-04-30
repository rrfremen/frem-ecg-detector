# built-in
from collections import deque
from multiprocessing import shared_memory
import importlib
import pkgutil

# external
import numpy as np

# internal
from .detector.detector_base import BaseDetector
from . import detector as detector_pkg
from .preprocessor.preprocessor_base import BasePreprocessor
from . import preprocessor as preprocessor_pkg
from .extractor.extractor_base import BaseExtractor
from . import extractor as extractor_pkg


class ProcessingPipeline:
    def __init__(self, config:dict):
        self.config_global = config
        self.config_local = {}
        self.fs = self.config_global['recordings']['fs']

        # initiate extractor
        self.avail_extractors = self.get_available_modules('extractor', extractor_pkg, BaseExtractor)
        extractor_name = config.get('extractor', {}).get('active') or 'WFDBExtractor'
        self.extractor = self.avail_extractors.get(extractor_name, self.avail_extractors['WFDBExtractor'])()
        self.extractor.set_config(config)

        # initiate preprocessor
        self.avail_preprocessors = self.get_available_modules('preprocessor', preprocessor_pkg, BasePreprocessor)
        preprocessor_name = config.get('preprocessor', {}).get('active') or 'DefaultPreprocessor'
        self.preprocessor = self.avail_preprocessors.get(preprocessor_name, self.avail_preprocessors['DefaultPreprocessor'])()
        self.preprocessor.set_config(config=config)

        # initiate detector
        self.avail_detectors = self.get_available_modules('detector', detector_pkg, BaseDetector)
        detector_name = config.get('detector', {}).get('active') or 'DefaultDetector'
        self.detector = self.avail_detectors.get(detector_name, self.avail_detectors['DefaultDetector'])()
        self.detector.set_config(config=config)

        # bpm calculation
        self.beat_calculation_window = 5
        self.beat_timestamps = deque(maxlen=self.beat_calculation_window)

    def get_available_modules(self, class_name, pkg, base_class):
        available = {}
        for _, module_name, _ in pkgutil.iter_modules(pkg.__path__):
            if module_name == class_name + '_base':
                continue
            module = importlib.import_module(f'.{class_name}.{module_name}', package=__package__)
            for name, obj in vars(module).items():
                if isinstance(obj, type) and issubclass(obj, base_class) and obj is not base_class:
                    available[name] = obj
        return available

    def get_shm(self):
        shm_raw = shared_memory.SharedMemory(name=self.config_global['preprocessor']['shm']['name'], create=False)
        shm_ver = np.ndarray(shape=(1,), dtype=np.uint64, buffer=shm_raw.buf, offset=0)
        shm_arr = np.ndarray(
            shape=self.config_global['preprocessor']['shm']['shape'],
            dtype=np.float64,
            buffer=shm_raw.buf,
            offset=self.config_global['preprocessor']['shm']['version_bytes']
        )
        return shm_raw, shm_ver, shm_arr

    def calculate_bpm(self, beat_timestamp):
        self.beat_timestamps.append(beat_timestamp)

        if len(self.beat_timestamps) < 2:
            return 1

        intervals = [
            self.beat_timestamps[i] - self.beat_timestamps[i - 1]
            for i in range(1, len(self.beat_timestamps))
        ]

        avg_interval = sum(intervals)/len(intervals)
        return 60/avg_interval

    def run(self, pipe_processing):
        process_running, process_paused = True, False
        print('starting processing pipeline')

        # windows and indexes
        sample_index = 0
        batch_index, batch_window = 0, int(self.fs / self.config_global['preprocessor']['batch_window'])  # 20 ms batch

        # data holder
        index_dq = deque([0] * self.fs, maxlen=self.fs)
        signal_dq = deque([0] * self.fs, maxlen=self.fs)
        signal_processed_dq = deque([0] * self.fs, maxlen=self.fs)
        detector_dq = deque([0] * self.fs, maxlen=self.fs)
        beat_location_dq = deque([0] * self.fs, maxlen=self.fs)
        bpm_dq = deque([0] * self.fs, maxlen=self.fs)
        result_holder = np.zeros(self.config_global['preprocessor']['shm']['shape'])

        # shared memory assignments
        shm_raw, shm_ver, shm_arr = self.get_shm()
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
            signal_dq.append(self.extractor.next_sample())

            # pre-processing stuff
            processed_sample = self.preprocessor.preprocess(signal_dq[-1])
            signal_processed_dq.append(processed_sample)

            # detector
            det, beat_loc = self.detector.detect(detector_dq[-1], np.asarray(signal_processed_dq))
            detector_dq.append(det)
            beat_location_dq.append(beat_loc)
            if beat_loc:
                beat_timestamp = sample_index/self.fs
                current_bpm = self.calculate_bpm(beat_timestamp)
                bpm_dq.append(current_bpm)
            else:
                bpm_dq.append(0)

            # result
            if sample_index < self.fs:
                sample_index += 1
                continue

            if batch_index >= batch_window:
                shm_ver[0] += 1  # odd number - writing
                # ecg data here
                result_holder[:, 0] = np.asarray(index_dq)
                result_holder[:, 1] = np.asarray(signal_dq)
                result_holder[:, 2] = np.asarray(signal_processed_dq)
                result_holder[:, 3] = np.asarray(detector_dq)
                result_holder[:, 4] = np.asarray(beat_location_dq)
                result_holder[:, 5] = np.asarray(bpm_dq)
                shm_arr[:] = result_holder
                shm_ver[0] += 1  # even number - version is stable

                pipe_processing.send('data_available')
                batch_index = 0

            batch_index += 1
            sample_index += 1
