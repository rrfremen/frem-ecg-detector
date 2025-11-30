# external
from PySide6.QtWidgets import QWidget

# private
from gui.plotter_side_ui import Ui_Form
from parents.thread_manager import ThreadManager


class PlotterSideWidget(QWidget, ThreadManager, Ui_Form):
    className = 'PlotterSideWidget'

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # shared variables
        self.config = None
