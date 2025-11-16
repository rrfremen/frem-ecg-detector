# internal
import logging
from datetime import datetime


class LogManager:
    def __init__(self):
        super().__init__()
        self.name = f'LOGGER - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}'
        self.logger = logging.getLogger(self.name)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def debug(self, msg): self.logger.debug(msg)
    def info(self, msg): self.logger.info(msg)
    def warning(self, msg): self.logger.warning(msg)
    def error(self, msg): self.logger.error(msg)
    def critical(self, msg): self.logger.critical(msg)


# TODO: eventually combine all parents class into one script for readability
