# external
from PySide6.QtWidgets import QWidget

# internal
from gui.plotter_side_ui import Ui_Form


class PlotterSideWidget(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
