# internal
import sys

# external
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QApplication, QSizePolicy

# private
from controller_widget import ControllerWidget
from plotter_main_widget import PlotterMainWidget
from plotter_side_widget import PlotterSideWidget
from parents.thread_manager import ThreadManager


class MainWindow(QMainWindow, ThreadManager):
    className = "MainWindow"

    def __init__(self):
        super().__init__()

        self.plotter_main = PlotterMainWidget()
        self.plotter_side = PlotterSideWidget()
        self.controller = ControllerWidget()

        self._setupUI()

    def _setupUI(self):
        # plotter
        plotter_layout = QHBoxLayout()
        self.plotter_main.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plotter_side.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        plotter_layout.addWidget(self.plotter_main)
        plotter_layout.addWidget(self.plotter_side)
        plotter_layout.setStretch(0, 3)
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())
