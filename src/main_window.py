# internal
from multiprocessing import Lock, Process, Pipe, Event
from threading import Thread
import json

# external
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy
from PySide6.QtCore import Signal, QTimer

# private
from controller_widget import ControllerWidget
from plotter_main_widget import PlotterMainWidget
from plotter_side_widget import PlotterSideWidget
from parents.thread_manager import ThreadManager
from algorithms.processing_pipeline import ProcessingPipeline


class MainWindow(QMainWindow, ThreadManager):
    className = "MainWindow"

    lock_config_global = Lock()
    signal_display_recs = Signal()
    signal_live_plot_start = Signal()
    signal_live_plot_pause = Signal()
    signal_live_plot_stop = Signal()
    event_live_plot = Event()

    def __init__(self):
        super().__init__()

        # shared variables
        with open('config_global.json', 'r') as f:
            self.config_global = json.load(f)

        # local variables

        # widgets
        controller_vars = {
            # config
            'lock_config_global': self.lock_config_global,
            'get_config': self.get_config,
            'overwrite_config': self.overwrite_config,
            # signal
            'display_recs': self.signal_display_recs,
            'signal_live_plot_start': self.signal_live_plot_start,
            'signal_live_plot_pause': self.signal_live_plot_pause,
            'signal_live_plot_stop': self.signal_live_plot_stop,
        }

        plotter_main_vars = {

        }

        plotter_side_vars = {
            # config
            'lock_config_global': self.lock_config_global,
            'get_config': self.get_config,
            'overwrite_config': self.overwrite_config,
        }

        self.plotter_main = PlotterMainWidget(plotter_main_vars)
        self.plotter_side = PlotterSideWidget(plotter_side_vars)
        self.controller = ControllerWidget(controller_vars)

        self.main_children = [self.plotter_main, self.plotter_side, self.controller]

        self.timer_main_plotter = QTimer()
        self.data_current_main_plotter = []

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
        self.signal_live_plot_start.connect(self.live_plot_start)
        self.signal_live_plot_pause.connect(self.live_plot_pause)
        self.signal_live_plot_stop.connect(self.live_plot_stop)

    # config functions
    def get_config(self):
        return self.config_global

    def overwrite_config(self, config):
        self.config_global = config
        for current_child in self.main_children:
            current_child.config_global = self.config_global  # update for all widgets
        print('config updated')

    # GUI functions
    def display_recs(self):
        self.controller.update_gui_file_selection()
        self.plotter_main.update_first_plot()

    def live_plot_start(self):
        # pipe for communication with external process
        pipe_processing, pipe_plotting = Pipe()

        # start a background thread to monitor incoming data from external process
        thread_pipe_plotting_monitor = Thread(
            name='Thread-Pipe-Plotting-Monitor',
            target=self.pipe_plotting_monitor,
            args=(pipe_plotting,)
        )
        # start an external process for data processing
        processing_pipeline = ProcessingPipeline(self.config_global)
        process_processing = Process(
            name='Process-Detector',
            target=processing_pipeline.run,
            args=(pipe_processing,)
        )
        # start all
        self.event_live_plot.set()
        process_processing.start()
        thread_pipe_plotting_monitor.start()

        # start a QTimer for updating main plotter
        # self.timer_main_plotter.setInterval(int(1000/self.config_global['display']['refresh_rate']))  # refresh rate in ms
        self.timer_main_plotter.setInterval(5000)
        self.timer_main_plotter.timeout.connect(self.live_plot_update)
        self.timer_main_plotter.start()

    def live_plot_update(self):
        print('update live plot triggered')

    def live_plot_pause(self):
        print('live plot paused')

    def live_plot_stop(self):
        pass

    # pipe stuff
    def pipe_plotting_monitor(self, pipe_plotting):
        print('monitor - started')
        new_data = None
        while self.event_live_plot.is_set():
            try:
                new_data = pipe_plotting.recv()  # blocking behaviour
                if type(new_data) in [int, float, list]:
                    self.data_current_main_plotter.append(new_data)
                elif type(new_data) is None:  # close the pipe
                    self.event_live_plot.clear()
                    pipe_plotting.close()
                else:
                    print('WARNING - unknown data received')
            except EOFError:
                # print('WARNING - processing pipe was closed unexpectedly')
                break
            else:
                pass