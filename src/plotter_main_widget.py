# external
from PySide6.QtWidgets import QWidget, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import numpy as np

# private
from gui.plotter_main_ui import Ui_Form
from parents.thread_manager import ThreadManager


class PlotterMainWidget(QWidget, ThreadManager, Ui_Form):
    className = 'PlotterMainWidget'

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setup_local_ui()

        # self.ax = self.figure.add_subplot(111)
        # self.x_data = np.arange(0, 2*np.pi, 0.1)
        # self.y_data = np.sin(self.x_data)
        # self.line, = self.ax.plot(self.x_data, self.y_data)

        # self.animation = FuncAnimation(self.figure, self.update_plot, frames=None, interval=100, repeat=False)

    def setup_local_ui(self):
        # FigureCanvas for main window
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.gridLayout_2.addWidget(self.canvas)

    def update_plot(self, frame):
        # self.x_data += 0.1
        # self.y_data = np.sin(self.x_data + frame * 0.1)
        # self.line.set_xdata(self.x_data)
        # self.line.set_ydata(self.y_data)
        # self.ax.set_xlim(self.x_data[0], self.x_data[0] + 10)
        self.canvas.draw()