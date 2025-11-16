# external
from PySide6.QtWidgets import QWidget

# internal
from gui.controller_ui import Ui_Form


class ControllerWidget(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
