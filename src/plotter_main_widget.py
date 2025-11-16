# external
from PySide6.QtWidgets import QWidget

# internal
from gui.plotter_main_ui import Ui_Form


class PlotterMainWidget(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
