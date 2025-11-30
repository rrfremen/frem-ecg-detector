from scipy.signal import butter, filtfilt


class FreqFilter:
    def __init__(self,
                 signal:list,
                 fs:int,
                 filter_type: str,
                 order:int=4,
                 lower_limit:float=0,
                 upper_limit:float=0.1):
        if signal is None:
            signal = []

        b, a = butter(N=order, Wn=[lower_limit, upper_limit], fs=fs, btype=filter_type)
        signal = filtfilt(b, a, signal)
