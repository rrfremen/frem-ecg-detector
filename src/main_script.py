# internal
import sys
from multiprocessing import Lock, Process, Pipe
from threading import Thread
import json

# external
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QApplication, QSizePolicy
from PySide6.QtCore import Signal

# private
from controller_widget import ControllerWidget
from plotter_main_widget import PlotterMainWidget
from plotter_side_widget import PlotterSideWidget
from parents.thread_manager import ThreadManager
from algorithms.processing_pipeline import ProcessingPipeline


class MainWindow(QMainWindow, ThreadManager):
    className = "MainWindow"

    central_config_lock = Lock()
    signal_display_recs = Signal()
    signal_start_live_plot = Signal()
    signal_update_live_plot = Signal()

    def __init__(self):
        super().__init__()

        # shared variables
        with open('central_config.json', 'r') as f:
            self.config = json.load(f)
            # get refresh rate of screen
            self.config['display']['refresh_rate'] = int(QGuiApplication.primaryScreen().refreshRate())

        # local variables

        # widgets
        controller_vars = {
            # config
            'central_config_lock': self.central_config_lock,
            'get_config': self.get_config,
            'overwrite_config': self.overwrite_config,
            # signal
            'display_recs': self.signal_display_recs,
            'start_live_plot': self.signal_start_live_plot
        }

        plotter_main_vars = {

        }

        self.plotter_main = PlotterMainWidget(plotter_main_vars)
        self.plotter_side = PlotterSideWidget()
        self.controller = ControllerWidget(controller_vars)

        self.main_children = [self.plotter_main, self.plotter_side, self.controller]

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
        self.signal_start_live_plot.connect(self.start_live_plot)

    # config functions
    def get_config(self):
        return self.config

    def overwrite_config(self, config):
        self.config = config
        for current_child in self.main_children:
            current_child.config = self.config  # update for all widgets
        print('config updated')

    # GUI functions
    def display_recs(self):
        print('main script received signal')
        self.controller.update_gui_file_selection()
        self.plotter_main.update_first_plot()

    def start_live_plot(self):
        pipe_processing, pipe_plotting = Pipe()
        print('here')
        thread_pipe_plotting_monitor = Thread(
            name='Thread-Pipe-Plotting-Monitor',
            target=self.pipe_plotting_monitor,
            args=(pipe_plotting,)
        )
        processing_pipeline = ProcessingPipeline(self.config)
        process_processing = Process(
            name='Process-Detector',
            target=processing_pipeline.run,
            args=(pipe_processing,)
        )
        process_processing.start()
        thread_pipe_plotting_monitor.start()

    def pipe_plotting_monitor(self, pipe_plotting):
        print('thread ok')


if __name__ == '__main__':
    # import multiprocessing
    # multiprocessing.set_start_method('spawn')
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())
