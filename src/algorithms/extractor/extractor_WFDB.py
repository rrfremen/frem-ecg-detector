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

    def next_sample(self) -> float:
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

