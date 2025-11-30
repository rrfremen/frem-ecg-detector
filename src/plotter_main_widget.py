# external
from PySide6.QtWidgets import QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import wfdb

# private
from gui.plotter_main_ui import Ui_Form


class PlotterMainWidget(QWidget, Ui_Form):
    className = 'PlotterMainWidget'

    def __init__(self, plotter_main_vars):
        super().__init__()
        self.setupUi(self)
        self.setup_local_ui()
        self.setup_signal(plotter_main_vars)

        # shared variables
        self.config = None

        # local variables

        # self.ax = self.figure.add_subplot(111)
        # self.x_data = np.arange(0, 2*np.pi, 0.1)
        # self.y_data = np.sin(self.x_data)
        # self.line, = self.ax.plot(self.x_data, self.y_data)

        # self.animation = FuncAnimation(self.figure, self.start_plotting, frames=None, interval=100, repeat=False)

    # setup functions
    def setup_local_ui(self):
        # FigureCanvas for main window
        self.figure_top = Figure()
        self.canvas_top = FigureCanvas(self.figure_top)
        self.plot_top = self.figure_top.add_subplot(111)
        self.plot_top.set_visible(False)

        self.figure_bottom = Figure()
        self.canvas_bottom = FigureCanvas(self.figure_bottom)
        self.plot_bottom = self.figure_bottom.add_subplot(111)

        self.gridLayout_2.addWidget(self.canvas_top)
        # self.gridLayout_2.addWidget(self.canvas_bottom)

    def setup_signal(self, plotter_main_vars):
        pass

    # Main Plotter GUI functions - Only use from main_script for centralization
    def update_first_plot(self):
        # self.gridLayout_2.removeWidget(self.canvas_bottom)
        # self.canvas_bottom.setParent(None)
        self.plot_top.set_visible(True)
        window = 10
        first_path = self.config['recordings']['paths'][0]
        signal = wfdb.rdsamp(first_path)[0][:window*self.config['recordings']['fs'], 0]
        time_index = np.arange(len(signal)) / self.config['recordings']['fs']
        self.plot_top.plot(time_index, signal)
        self.plot_top.grid()
        self.plot_top.set_xlabel('Time in s')
        self.plot_top.set_ylabel('Amplitude in mV')
        self.canvas_top.draw()

    # internal functions
    def start_plotting(self):
        self.canvas_top.draw()
