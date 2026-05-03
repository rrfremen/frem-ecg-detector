# built-in
from pathlib import Path

# external
import wfdb

# internal
from .extractor_base import BaseExtractor


class WFDBExtractor(BaseExtractor):
    def __init__(self):
        super().__init__()

        # external values
        self.recording_path = None
        self.channel = None

        # internal values
        self.recording = None
        self.raw_signal = None
        self.index = 0

    # live extractor functions
    def set_config(self, config: dict):
        self.recording_path = config['extractor'].get('params', {}).get('active_path', "")
        self.channel = config['extractor'].get('params', {}).get('active_channel', 0)

        self.extract_recording()

    def update_config(self, key: str, value):
        pass

    def next_sample(self) -> float | None:
        if self.index >= len(self.raw_signal):
            return None
        sample = self.raw_signal[self.index]
        self.index += 1
        return sample

    def override_index(self, index):
        self.index = index

    # internal functions
    def extract_recording(self):
        if not self.recording_path:
            raise ValueError('No file selected')
        self.recording = wfdb.rdrecord(self.recording_path)
        channel_index = self.recording.sig_name.index(self.channel) if self.channel in self.recording.sig_name else 0
        self.raw_signal = self.recording.p_signal[:, channel_index]

    # external functions (non-pipeline usage)
    @staticmethod
    def extract_metadata_from_file(current_path: str) -> tuple[list, int, list]:
        if Path(current_path + '.hea').exists():  # faster with header only
            current_header = wfdb.rdheader(current_path)
        else:
            current_header = wfdb.rdrecord(current_path)

        return current_header.sig_name, current_header.fs, current_header.units

    @staticmethod
    def extract_signal_snippet(signal_path: str, fs: int, length: int, channel_index: int):
        signal_raw = wfdb.rdsamp(signal_path)
        signal = signal_raw[0][:length * fs, channel_index]

        return signal, signal_raw[1]['sig_len']
