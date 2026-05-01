from abc import ABC, abstractmethod


class BaseExtractor(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def set_config(self, config: dict):
        pass

    @abstractmethod
    def update_config(self, key: str, value):
        pass

    @abstractmethod
    def next_sample(self) -> float | None:
        pass

    @abstractmethod
    def override_index(self, index):
        pass
