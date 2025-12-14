import numpy as np
from scipy.signal import butter, filtfilt
import time


class ProcessingPipeline:
    def __init__(self, config:dict):
        pass

    def run(self, pipe_processing):
        print('process started')
        time.sleep(5)
        pipe_processing.send('this is a message from external process')
        time.sleep(5)
        pipe_processing.send('this is another message 5 seconds after')
