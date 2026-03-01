# external
from PySide6.QtWidgets import QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
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

        # self.ax = self.figure.add_subplot(111)
        # self.x_data = np.arange(0, 2*np.pi, 0.1)
        # self.y_data = np.sin(self.x_data)
        # self.line, = self.ax.plot(self.x_data, self.y_data)

        # self.animation = FuncAnimation(self.figure, self.start_plotting, frames=None, interval=100, repeat=False)

    # setup functions
    def setup_local_ui(self):
        # FigureCanvas for main window
        self.figure_upper = Figure()
        self.canvas_upper = FigureCanvas(self.figure_upper)
        self.plot_upper = self.figure_upper.add_subplot(111)
        self.plot_upper.set_visible(False)

        self.figure_lower = Figure()
        self.canvas_lower = FigureCanvas(self.figure_lower)
        self.plot_lower = self.figure_lower.add_subplot(111)
        self.plot_lower.set_visible(False)

        self.gridLayout_2.addWidget(self.canvas_upper)
        # self.gridLayout_2.addWidget(self.canvas_lower)

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
        # self.gridLayout_2.removeWidget(self.canvas_lower)
        # self.canvas_lower.setParent(None)
        self.plot_upper.set_visible(True)
        first_path = self.config_global['recordings']['paths'][0]
        signal = wfdb.rdsamp(first_path)[0][:self.plot_window*self.config_global['recordings']['fs'], 0]
        time_index = np.arange(len(signal)) / self.config_global['recordings']['fs']
        self.plot_upper.plot(time_index, signal)
        self.plot_upper.grid()
        self.plot_upper.set_xlabel('Time in s')
        self.plot_upper.set_ylabel('Amplitude in mV')
        self.canvas_upper.draw()

    # internal functions
    def live_plot_update(self):
        # temporarily for one plot only
        if np.any(self.data_ring_buffer[:, 0]):
            current_index = int(np.argmax(self.data_ring_buffer[:, 0]))
            window = 10*360
            if current_index - window > 0:
                current_signal = self.data_ring_buffer[current_index-window:current_index, 1]
            else:
                current_signal = self.data_ring_buffer[0:current_index, 1]
            self.plot_upper.cla()
            self.plot_upper.plot(current_signal)
            self.plot_upper.relim()
            self.plot_upper.autoscale_view()
            self.plot_upper.grid()
            self.plot_upper.set_xlabel('Samples')
            self.plot_upper.set_ylabel('Amplitude in mV')
            self.canvas_upper.draw()
