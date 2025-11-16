# external
from PySide6.QtWidgets import QWidget

# private
from gui.plotter_main_ui import Ui_Form
from parents.thread_manager import ThreadManager


class PlotterMainWidget(QWidget, ThreadManager, Ui_Form):
    className = 'PlotterMainWidget'

    def __init__(self):
        super().__init__()
        self.setupUi(self)
