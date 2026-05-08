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
from .math_utils import ms_to_fs


class ProcessingPipeline:
    def __init__(self, config:dict):
        self.config_global = config
        self.config_local = {}
        self.fs = 0

        self.default_modules = {
            'extractor': 'WFDBExtractor',
            'preprocessor': 'DefaultPreprocessor',
            'detector': 'DefaultDetector'
        }

        # get available modules
        self.avail_extractors = self.get_available_modules('extractor', extractor_pkg, BaseExtractor)
        self.avail_preprocessors = self.get_available_modules('preprocessor', preprocessor_pkg, BasePreprocessor)
        self.avail_detectors = self.get_available_modules('detector', detector_pkg, BaseDetector)

        self.extractor, self.preprocessor, self.detector = None, None, None

        # bpm calculation
        self.beat_calculation_window = 5
        self.beat_timestamps = deque(maxlen=self.beat_calculation_window)

    # noinspection PyMethodMayBeStatic
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

    def assign_module(self, module_type, module_avails):
        module_name = self.config_global.get(module_type, {}).get('active') or self.default_modules[module_type]
        module = module_avails.get(module_name, module_avails[self.default_modules[module_type]])()
        module.set_config(self.config_global)
        setattr(self, module_type, module)

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
        process_running, process_paused = False, False

        # None initialization to suppress unbounded local variables warnings
        shm_raw, shm_ver, shm_arr, result_holder = None, None, None, None
        index_dq, signal_dq, signal_processed_dq = None, None, None
        detector_dq, beat_location_dq, bpm_dq = None, None, None
        sample_index, batch_index, batch_window = 0, 0, 0

        # noinspection PyBroadException
        try:
            self.fs = self.config_global['extractor']['fs']

            result_holder = np.zeros(self.config_global['preprocessor']['shm']['shape'])

            # shared memory assignments
            shm_raw, shm_ver, shm_arr = self.get_shm()
            shm_ver[0] = 0  # initialize version

            # assign modules
            self.assign_module('extractor', self.avail_extractors)
            self.assign_module('preprocessor', self.avail_preprocessors)
            self.assign_module('detector', self.avail_detectors)

            process_running = True
        except Exception:
            pipe_processing.send('pipeline_failed_start')

        if process_running:
            # windows and indexes
            sample_index = 0
            batch_index = 0
            batch_window = ms_to_fs(
                self.fs,
                self.config_global['preprocessor']['batch_window']
            )

            # data holder
            index_dq = deque([0] * self.fs, maxlen=self.fs)
            signal_dq = deque([0] * self.fs, maxlen=self.fs)
            signal_processed_dq = deque([0] * self.fs, maxlen=self.fs)
            detector_dq = deque([0] * self.fs, maxlen=self.fs)
            beat_location_dq = deque([0] * self.fs, maxlen=self.fs)
            bpm_dq = deque([0] * self.fs, maxlen=self.fs)
            pipe_processing.send('pipeline_starting')  # send handshake confirmation

        while process_running:
            # check for any command from GUI
            if pipe_processing.poll() and not process_paused:
                signal_from_gui = pipe_processing.recv()
                if isinstance(signal_from_gui, str):
                    if signal_from_gui == 'Pause':
                        process_paused = True
                    elif signal_from_gui == 'Stop':
                        break
            elif process_paused:  # block the loop if paused
                signal_from_gui = pipe_processing.recv()
                if isinstance(signal_from_gui, str):
                    if signal_from_gui == 'Continue':
                        process_paused = False
                    elif signal_from_gui == 'Stop':
                        break

            # pass on sample index and ecg sample to their ring buffer
            next_sample = self.extractor.next_sample()

            if next_sample is None:
                pipe_processing.send('pipeline_finished_and_paused')
                process_paused = True
                continue

            index_dq.append(sample_index)
            signal_dq.append(next_sample)

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
