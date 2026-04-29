#internal
import sys
import logging

# external
from PySide6.QtWidgets import QApplication

# private
from src.main_window import MainWindow


def logger_init():
    # silence logs from external libraries
    logging.getLogger().setLevel(logging.CRITICAL + 1)

    # app logger
    logger_app = logging.getLogger('app')
    logger_app.setLevel(logging.DEBUG)
    logger_app.propagate = False

    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    file_handler = logging.FileHandler('frem-ecg-detector.log', mode='w')
    console_handler = logging.StreamHandler()
    file_handler.setFormatter(log_format)
    console_handler.setFormatter(log_format)

    logger_app.addHandler(file_handler)
    logger_app.addHandler(console_handler)


if __name__ == '__main__':
    # initiate logger for the application
    logger_init()
    logger = logging.getLogger('app.' + __name__)
    logger.info('frem-ecg-detector starting')

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())
