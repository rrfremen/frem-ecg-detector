# internal
from multiprocessing import Lock, Process, Pipe, Event, shared_memory
from threading import Thread
import json
import logging
from pathlib import Path

# external
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy
from PySide6.QtCore import Signal, QTimer
import numpy as np

# private
from .controller_widget import ControllerWidget
from .plotter_main_widget import PlotterMainWidget
from .plotter_side_widget import PlotterSideWidget
from .parents.thread_manager import ThreadManager
from .algorithms.processing_pipeline import ProcessingPipeline


class MainWindow(QMainWindow, ThreadManager):
    className = "MainWindow"

    signal_display_recs = Signal()
    signal_live_plot_start = Signal()
    signal_live_plot_pause = Signal()
    signal_live_plot_continue = Signal()
    signal_live_plot_stop = Signal()

    def __init__(self):
        super().__init__()

        # locks and events
        self.lock_config_global = Lock()
        self.lock_live_plot_data = Lock()
        self.lock_live_plot_monitor = Lock()
        self.event_live_plot = Event()

        # shared variables
        config_global_path = Path(__file__).parent / 'config_global.json'
        with open(config_global_path, 'r') as f:
            self.config_global = json.load(f)

        # local variables
        self.pipe_processing = None
        self.logger = logging.getLogger('app.' + __name__)

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
            'signal_live_plot_continue': self.signal_live_plot_continue,
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

        self.setup_ui_local()
        self.setup_signal()
        self.logger.info("This is main window")

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
        self.signal_live_plot_continue.connect(self.live_plot_continue)
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
        # block live monitor to start running directly as a safeguard
        self.lock_live_plot_monitor.acquire(block=True)
        # pipe for communication with external process
        pipe_processing, self.pipe_processing = Pipe()

        # internal function for safeguard again shared memory leaks
        def create_shm(name: str, size: int):
            # remove if old SHM exists
            try:
                old_shm = shared_memory.SharedMemory(name=name, create=False)
                old_shm.close()
                old_shm.unlink()
            except FileNotFoundError:
                pass

            return shared_memory.SharedMemory(name=name, create=True, size=size)

        # shared memory for data transfer between processes
        shm_name = 'ecg-shm'
        shm_shape = (self.config_global['recordings']['fs'],
                     len(self.config_global['recordings']['channels_in_use'])+3)
        shm_data_bytes = int(np.prod(shm_shape) * np.dtype(np.float64).itemsize)
        shm_version_bytes = np.dtype(np.uint64).itemsize
        shm_raw = create_shm(name=shm_name, size=(shm_data_bytes + shm_version_bytes))

        self.config_global['preprocessing']['shm'].update({
            'name': shm_name,
            'shape': shm_shape,
            'data_bytes': shm_data_bytes,
            'version_bytes': shm_version_bytes
        })
        self.overwrite_config(self.config_global)
        self.plotter_main.ring_buffer_setup()

        # start a background thread to monitor incoming data from external process
        thread_worker_pipe_processing_monitor = Thread(
            name='Thread-Pipe-Plotting-Monitor',
            target=self.worker_pipe_processing_monitor,
            args=(self.pipe_processing, shm_raw)
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
        thread_worker_pipe_processing_monitor.start()

        # unlink shared memory directly now to avoid orphaned memory later
        # TODO eventually move this to prevent GUI blocking
        processing_handshake = self.pipe_processing.recv()
        if processing_handshake == 'shm_attached':
            shm_raw.unlink()
            self.timer_main_plotter.setInterval(int(1000/self.config_global['plotter']['display']['refresh_rate']))  # refresh rate in ms
            # self.timer_main_plotter.setInterval(5000)
            self.timer_main_plotter.timeout.connect(self.live_plot_update)
            self.timer_main_plotter.start()
            self.lock_live_plot_monitor.release()
            self.logger.info('SHM handshake from processing pipeline confirmed')
        else:
            ValueError('processing pipeline gave no handshake')

    def live_plot_update(self):
        with self.lock_live_plot_data:
            self.plotter_main.live_plot_update()

    def live_plot_pause(self):
        self.pipe_processing.send('Pause')

    def live_plot_continue(self):
        self.pipe_processing.send('Continue')

    def live_plot_stop(self):
        pass

    # pipe stuff
    def worker_pipe_processing_monitor(self, pipe_plotting, shm_raw):
        new_data = None
        shm_ver = np.ndarray(shape=(1,), dtype=np.uint64, buffer=shm_raw.buf, offset=0)
        shm_arr = np.ndarray(
            shape=self.config_global['preprocessing']['shm']['shape'],
            dtype=np.float64,
            buffer=shm_raw.buf,
            offset=self.config_global['preprocessing']['shm']['version_bytes']
        )
        prev_indexes, new_indexes = None, []
        with self.lock_live_plot_monitor:
            self.logger.info('Monitor Thread starting')
        while self.event_live_plot.is_set():
            try:
                new_data = pipe_plotting.recv()  # blocking behaviour
                if type(new_data) == str:
                    if new_data == 'data_available':
                        for _ in range(3):  # small retry loop
                            v1 = shm_ver[0]  # version check to prevent copying while something is being written
                            if v1 & 1:
                                continue
                            new_snapshot = shm_arr.copy()
                            v2 = shm_ver[0]
                            if v1 == v2 and not (v2 & 1):
                                # get only new data from snapshot and send it to plotter_main_widget
                                if prev_indexes is not None:
                                    new_indexes = new_snapshot[:, 0].copy()
                                    shift_front = int(new_indexes[0] - prev_indexes[0])
                                    shift_end = int(new_indexes[-1] - prev_indexes[-1])
                                    if shift_front == shift_end and shift_front < self.config_global['recordings']['fs']:
                                        if shift_front <= self.config_global['recordings']['fs']//2:
                                            new_data = new_snapshot[-shift_front:, :]
                                            with self.lock_live_plot_data:
                                                self.plotter_main.ring_buffer_update(new_data)
                                    else:
                                        self.logger.warning('Data shifted irregularly')
                                    prev_indexes = new_indexes.copy()
                                else:
                                    new_data = new_snapshot
                                    with self.lock_live_plot_data:
                                        self.plotter_main.ring_buffer_update(new_data)
                                    prev_indexes = new_snapshot[:, 0].copy()
                elif new_data is None:  # close the pipe
                    self.event_live_plot.clear()
                    pipe_plotting.close()
                else:
                    self.logger.warning(f'Monitoring Pipeline received unknown data: {new_data}')
            except EOFError:
                # print('WARNING - processing pipe was closed unexpectedly')
                break
            else:
                pass