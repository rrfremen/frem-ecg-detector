# external
from PySide6.QtWidgets import QWidget

# private
from gui.plotter_side_ui import Ui_Form


class PlotterSideWidget(QWidget, Ui_Form):
    className = 'PlotterSideWidget'

    def __init__(self):
        super().__init__()
        self.setupUi(self)
