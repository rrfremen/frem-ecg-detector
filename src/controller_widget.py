# external
from PySide6.QtWidgets import QWidget

# private
from gui.controller_ui import Ui_Form
from parents.thread_manager import ThreadManager


class ControllerWidget(QWidget, ThreadManager, Ui_Form):
    className = 'ControllerWidget'

    def __init__(self):
        super().__init__()
        self.setupUi(self)
