# built-in
import time

# external
from PySide6.QtWidgets import QWidget, QProgressBar
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

        self.bpm_prev = 0

        self.buffer_index = 0

    # setup functions
    def setup_local_ui(self):
        # upper plot
        self.plot_upper = pg.PlotWidget()
        self.plot_upper.showGrid(x=True, y=True)
        self.plot_upper.setLabel('left', 'Amplitude', units='mV')
        self.plot_upper.setLabel('bottom', 'Time', units='s')
        self.plot_upper.setMouseEnabled(x=False, y=False)

        self.line_signal = self.plot_upper.plot()

        # lower plot
        self.plot_lower = pg.PlotWidget()
        self.plot_lower.showGrid(x=True, y=True)
        self.plot_lower.setLabel('left', 'Amplitude', units='mV^2')
        self.plot_lower.setLabel('bottom', 'Time', units='s')
        self.plot_lower.setMouseEnabled(x=False, y=False)

        self.line_processed = self.plot_lower.plot()
        self.circle_beat = self.plot_lower.plot(pen=None, symbol='o', symbolSize=8, symbolBrush='#F70505')
        self.line_detector = self.plot_lower.plot()

        # progress widget
        self.progress_widget = OverlayProgressWidget()

        # layout
        self.gridLayout_2.addWidget(self.plot_upper, 0, 0)
        self.gridLayout_2.addWidget(self.plot_lower, 1, 0)
        self.gridLayout_2.addWidget(self.progress_widget)
        self.gridLayout_2.setRowStretch(0, 1)

        self.plot_upper.getAxis('left').setWidth(50)
        self.plot_lower.getAxis('left').setWidth(50)

        self.plot_lower.setVisible(False)

    def setup_signal(self, plotter_main_vars):
        self.signal_plotters_bpm = plotter_main_vars['signal_plotters_bpm']

    def ring_buffer_setup(self):
        self.ring_buffer_capacity = self.config_global['recordings']['fs'] * 60 * self.config_global['plotter']['buffer']['capacity']
        self.data_ring_buffer = np.zeros((self.ring_buffer_capacity, self.config_global['preprocessor']['shm']['shape'][1]), dtype=np.float64)

    def ring_buffer_update(self, data_from_pipeline):
        incoming_data_length = data_from_pipeline.shape[0]
        start_index = int(data_from_pipeline[0, 0] % self.ring_buffer_capacity)
        end_index = start_index + incoming_data_length

        self.buffer_index = data_from_pipeline[-1, 0]

        new_data = np.zeros_like(data_from_pipeline)
        shift_idx = np.flatnonzero(data_from_pipeline[:, 4])  # TODO - is flatnonzero effective
        bpm_idx = np.flatnonzero(data_from_pipeline[:, 5])

        new_data[:, :4] = data_from_pipeline[:, :4]

        if end_index <= self.ring_buffer_capacity:
            self.data_ring_buffer[start_index:end_index, :] = new_data
        else:
            first_part = self.ring_buffer_capacity - start_index
            self.data_ring_buffer[start_index:, :] = new_data[:first_part, :]
            self.data_ring_buffer[:end_index % self.ring_buffer_capacity, :] = new_data[first_part:, :]

        if shift_idx.size:
            shift_idx = shift_idx[0]
            shift_val = data_from_pipeline[shift_idx, 4]
            abs_idx = int((start_index + shift_idx + shift_val) % self.ring_buffer_capacity)
            self.data_ring_buffer[abs_idx, 4] = self.data_ring_buffer[abs_idx, 2]
            bpm = data_from_pipeline[bpm_idx[0], 5]
            self.data_ring_buffer[abs_idx, 5] = bpm

    # Main Plotter GUI functions - Only use from main_script for centralization
    def set_light_mode(self):
        self.plot_upper.setBackground('w')
        self.plot_lower.setBackground('w')
        self.plot_upper.getAxis('left').setTextPen('k')
        self.plot_upper.getAxis('bottom').setTextPen('k')
        self.plot_lower.getAxis('left').setTextPen('k')
        self.plot_lower.getAxis('bottom').setTextPen('k')

        self.line_signal.setPen('#1c10d1')
        self.line_processed.setPen('#1c10d1')
        self.line_detector.setPen('#d17810')

    def set_dark_mode(self):
        self.plot_upper.setBackground('k')
        self.plot_lower.setBackground('k')
        self.plot_upper.getAxis('left').setTextPen('w')
        self.plot_upper.getAxis('bottom').setTextPen('w')
        self.plot_lower.getAxis('left').setTextPen('w')
        self.plot_lower.getAxis('bottom').setTextPen('w')

        self.line_signal.setPen('#00d4ff')
        self.line_processed.setPen('#00d4ff')
        self.line_detector.setPen('#ff9c0f')

    def update_first_plot(self):
        self.plot_upper.setVisible(True)
        fs = self.config_global['recordings']['fs']
        first_path = self.config_global['recordings']['paths'][0]

        signal_raw = wfdb.rdsamp(first_path)[0]
        signal = signal_raw[:self.plot_window * fs, 0]
        time_index = np.arange(len(signal)) / fs

        self.line_signal.setData(time_index, signal)
        self.progress_widget.set_max(len(signal_raw))

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

    # external functions
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
        # dt_data = (current_index - self.plot_prev_index) / fs
        # print(f'dt real: {dt_real:.4f} | dt data: {dt_data:.4f}')
        self.plot_prev_index = current_index

        # handles wrap around at the end of ring buffer
        end = current_index % buffer_capacity
        start = (current_index - window) % buffer_capacity
        if start < end:
            segment = data_ring_buffer[start:end]
        else:
            segment = np.vstack((data_ring_buffer[start:], data_ring_buffer[:end]))

        # assign data to individual variables
        time_index = segment[:, 0] / fs
        current_signal = segment[:, 1]
        current_signal_processed = segment[:, 2]
        current_detector = segment[:, 3]
        current_beat = segment[:, 4]
        current_bpm = segment[:, 5]

        bpm_indexes = np.flatnonzero(current_bpm)
        if bpm_indexes.size:
            current_bpm = current_bpm[bpm_indexes[-1]]
            if self.bpm_prev != current_bpm:
                self.signal_plotters_bpm.emit(current_bpm)
                self.bpm_prev = current_bpm

        # upper plot
        self.line_signal.setData(time_index, current_signal)

        # lower plot
        if self.plot_lower.isVisible():
            self.line_processed.setData(time_index, current_signal_processed)
            circle_active = current_beat != 0
            self.circle_beat.setData(time_index[circle_active], current_beat[circle_active])

            if self.show_plot_detector:
                self.line_detector.setData(time_index, current_detector)
            else:
                self.line_detector.setData([], [])

        # progress bar
        self.progress_widget.update_progress_buffer(self.buffer_index)  # TODO - make independent of plot update
        self.progress_widget.update_progress_plotter(segment[-1, 0])


class OverlayProgressWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(20)

        self.progress_buffer = QProgressBar(self)
        self.progress_buffer.setObjectName('progress_buffer')

        self.progress_plotter = QProgressBar(self)
        self.progress_plotter.setObjectName('progress_plotter')
        self.progress_plotter.raise_()

    def resizeEvent(self, event):
        self.progress_buffer.setGeometry(self.rect())
        self.progress_plotter.setGeometry(self.rect())
        super().resizeEvent(event)

    def set_max(self, max_val):
        self.progress_buffer.setMaximum(max_val)
        self.progress_plotter.setMaximum(max_val)

    def update_progress_buffer(self, val):
        self.progress_buffer.setValue(val)

    def update_progress_plotter(self, val):
        self.progress_plotter.setValue(val)