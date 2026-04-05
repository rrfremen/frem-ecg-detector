# built-in
import time

# external
from PySide6.QtWidgets import QWidget
import pyqtgraph as pg
import numpy as np
import wfdb

# private
from .gui.plotter_main_ui import Ui_Form


class PlotterMainWidget(QWidget, Ui_Form):
    className = 'PlotterMainWidget'

    def __init__(self, global_config, plotter_main_vars):
        super().__init__()
        self.setupUi(self)
        self.setup_local_ui()
        self.setup_signal(plotter_main_vars)

        # shared variables
        self.config_global = global_config

        # local variables
        self.data_ring_buffer = []
        self.plot_window = 10
        self.ring_buffer_capacity = 1
        self.show_plot_detector = False
        self.current_index_timer = 0

        self.plot_timer_last_time = time.time()
        self.plot_prev_index = 0

    # setup functions
    def setup_local_ui(self):
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        # upper plot
        self.plot_upper = pg.PlotWidget()
        self.plot_upper.showGrid(x=True, y=True)
        self.plot_upper.setLabel('left', 'Amplitude', units='mV')
        self.plot_upper.setLabel('bottom', 'Time', units='s')

        self.line_signal = self.plot_upper.plot(pen='#1c10d1')

        # lower plot
        self.plot_lower = pg.PlotWidget()
        self.plot_lower.showGrid(x=True, y=True)
        self.plot_lower.setLabel('left', 'Amplitude', units='mV^2')
        self.plot_lower.setLabel('bottom', 'Time', units='s')

        self.line_processed = self.plot_lower.plot(pen='#1c10d1')
        self.line_detector = self.plot_lower.plot(pen='#d17810')

        # layout
        self.gridLayout_2.addWidget(self.plot_upper, 0, 0)
        self.gridLayout_2.addWidget(self.plot_lower, 1, 0)
        self.gridLayout_2.setRowStretch(0, 1)

        self.plot_lower.setVisible(False)

    def setup_signal(self, plotter_main_vars):
        pass

    def ring_buffer_setup(self):
        self.ring_buffer_capacity = self.config_global['recordings']['fs'] * 60 * self.config_global['plotter']['buffer']['capacity']
        self.data_ring_buffer = np.zeros((self.ring_buffer_capacity, self.config_global['preprocessing']['shm']['shape'][1]), dtype=np.float64)

    def ring_buffer_update(self, data_from_pipeline):
        incoming_data_length = data_from_pipeline.shape[0]
        start_index = int(data_from_pipeline[0, 0] % self.ring_buffer_capacity)
        end_index = start_index + incoming_data_length

        if end_index <= self.ring_buffer_capacity:
            self.data_ring_buffer[start_index:end_index, :] = data_from_pipeline
        else:
            first_part = self.ring_buffer_capacity - start_index
            self.data_ring_buffer[start_index:, :] = data_from_pipeline[:first_part, :]
            self.data_ring_buffer[:end_index % self.ring_buffer_capacity, :] = data_from_pipeline[first_part:, :]

    # Main Plotter GUI functions - Only use from main_script for centralization
    def update_first_plot(self):
        self.plot_upper.setVisible(True)
        fs = self.config_global['recordings']['fs']
        first_path = self.config_global['recordings']['paths'][0]

        signal = wfdb.rdsamp(first_path)[0][:self.plot_window * fs, 0]
        time_index = np.arange(len(signal)) / fs

        self.line_signal.setData(time_index, signal)

    def canvas_lower_plots_toggle(self, cmd):
        # TODO - update lower plot during pause
        def plot_lower_toggle():
            state_canvas_lower = not self.plot_lower.isVisible()
            self.plot_lower.setVisible(state_canvas_lower)
            self.gridLayout_2.setRowStretch(1, state_canvas_lower)
            # if self.plot_upper.get_visible():
            # self.plot_lower.set_visible(self.plot_upper.get_visible())
            if not state_canvas_lower:
                self.show_plot_detector = False

        if cmd == 'processed':
            plot_lower_toggle()
        elif cmd == 'detector':
            if not self.plot_lower.isVisible():
                plot_lower_toggle()
            self.show_plot_detector = not self.show_plot_detector

    # internal functions
    def live_plot_update(self, data_ring_buffer):
        fs = self.config_global['recordings']['fs']
        buffer_capacity = len(data_ring_buffer)
        window = self.plot_window * fs

        if not np.any(data_ring_buffer[:, 0]):
            return

        # get current time and get time lapsed inbetween
        time_now = time.time()
        dt_real = time_now - self.plot_timer_last_time
        self.plot_timer_last_time = time_now
        # calculate appropriate samples for the refresh rate
        samples_per_frame = fs * dt_real
        # get index for the amount of appropriate samples
        self.current_index_timer += samples_per_frame
        max_index = int(np.max(data_ring_buffer[:, 0]))
        # make sure index timer doesn't overshoot real data
        if self.current_index_timer > max_index:
            self.current_index_timer = max_index

        current_index = int(self.current_index_timer)
        if current_index <= self.plot_prev_index:
            return
        self.plot_prev_index = current_index

        # start = max(0, current_index - window)
        # segment = data_ring_buffer[start:current_index]

        # handles wrap around at the end of ring buffer
        end = current_index % buffer_capacity
        start = (current_index - window) % buffer_capacity
        if start < end:
            segment = data_ring_buffer[start:end]
        else:
            segment = np.vstack((data_ring_buffer[start:], data_ring_buffer[:end]))

        # dt_data = (current_index - self.plot_prev_index) / fs
        # print(f'dt real: {dt_real:.4f} | dt data: {dt_data:.4f}')

        # assign data to individual variables
        time_index = segment[:, 0] / fs
        current_signal = segment[:, 1]
        current_signal_processed = segment[:, 2]
        current_detector = segment[:, 3]

        # upper plot
        self.line_signal.setData(time_index, current_signal)

        # lower plot
        if self.plot_lower.isVisible():
            self.line_processed.setData(time_index, current_signal_processed)

            if self.show_plot_detector:
                self.line_detector.setData(time_index, current_detector)
            else:
                self.line_detector.setData([], [])
