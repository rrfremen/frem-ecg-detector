# internal
import sys
from multiprocessing import Lock
import json

# external
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QApplication, QSizePolicy
from PySide6.QtCore import Signal

# private
from controller_widget import ControllerWidget
from plotter_main_widget import PlotterMainWidget
from plotter_side_widget import PlotterSideWidget
from parents.thread_manager import ThreadManager


class MainWindow(QMainWindow, ThreadManager):
    className = "MainWindow"

    central_config_lock = Lock()
    signal_display_recs = Signal()

    def __init__(self):
        super().__init__()

        # global variables
        with open('central_config.json', 'r') as f:
            self.config = json.load(f)

        # local variables

        # widgets
        controller_signals = {
            # config
            'central_config_lock': self.central_config_lock,
            'get_config': self.get_config,
            'overwrite_config': self.overwrite_config,
            # signal
            'display_recs': self.signal_display_recs
        }

        self.plotter_main = PlotterMainWidget()
        self.plotter_side = PlotterSideWidget()
        self.controller = ControllerWidget(controller_signals)

        self.setup_ui_local()
        self.setup_signal()

    # setup functions
    def setup_ui_local(self):
        # plotter
        plotter_layout = QHBoxLayout()
        self.plotter_main.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plotter_side.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        plotter_layout.addWidget(self.plotter_main)
        plotter_layout.addWidget(self.plotter_side)
        plotter_layout.setStretch(0, 4)
        plotter_layout.setStretch(1, 1)
        plotter_widget = QWidget()
        plotter_widget.setLayout(plotter_layout)

        # plotter + controller
        self.controller.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        central_layout = QVBoxLayout()
        central_layout.addWidget(plotter_widget)
        central_layout.addWidget(self.controller)
        central_layout.setStretch(0, 3)
        central_layout.setStretch(1, 1)

        central_widget = QWidget()
        central_widget.setLayout(central_layout)

        self.setCentralWidget(central_widget)
        self.adjustSize()
        # self.setMinimumSize(800, self.plotter.height()+self.controller.height())

        # window
        self.setWindowTitle('ECG Detector')
        # self.setWindowIcon(QIcon.fromTheme('path'))

    def setup_signal(self):
        self.signal_display_recs.connect(self.display_recs)

    # config functions
    def get_config(self):
        return self.config

    def overwrite_config(self, config):
        self.config = config
        print('config updated')

    # GUI functions
    def display_recs(self):
        print('main script received signal')
        self.controller.update_gui_file_selection()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())
