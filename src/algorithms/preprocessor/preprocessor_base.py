from abc import ABC, abstractmethod


class BasePreprocessor(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def set_config(self, config: dict):
        pass

    @abstractmethod
    def update_config(self, key: str, value):
        pass

    @abstractmethod
    def preprocess(self, sample) -> float:
        pass
