from abc import ABC, abstractmethod


class BaseDetector(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def set_config(self, config: dict):
        pass

    @abstractmethod
    def update_config(self, key: str, value):
        pass

    @abstractmethod
    def detect(self, last_det, signal) -> tuple[float, int]:
        pass
