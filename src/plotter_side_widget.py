# built-in
from pathlib import Path

# external
from PySide6.QtWidgets import QWidget

# private
from .gui.plotter_side_ui import Ui_Form
from .parents.thread_manager import ThreadManager


class PlotterSideWidget(QWidget, ThreadManager, Ui_Form):
    className = 'PlotterSideWidget'

    def __init__(self, global_config, plotter_side_vars):
        super().__init__()
        self.setupUi(self)
        self.setup_signal(plotter_side_vars)

        # shared variables
        self.config_global = global_config

    def setup_signal(self, plotter_side_vars):
        pass

    # Side Plotter GUI Functions - Only use from main_Script for centralization
    def update_gui_file_selection(self):
        file_selected = self.config_global['recordings']['paths'][0]
        file_selected = Path(file_selected).name
        self.label_currentSource.setText(f'Source: {file_selected}.dat')
