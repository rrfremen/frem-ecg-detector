# built-in
from pathlib import Path

# external
from PySide6.QtWidgets import QWidget

# internal
from .gui.plotter_side_ui import Ui_Form


class PlotterSideWidget(QWidget, Ui_Form):
    className = 'PlotterSideWidget'

    def __init__(self, global_config, plotter_side_vars):
        super().__init__()
        self.setupUi(self)
        self.setup_signal(plotter_side_vars)

        # shared variables
        self.config_global = global_config

    def setup_signal(self, plotter_side_vars):
        self.signal_plotters_bpm = plotter_side_vars['signal_plotters_bpm']

        self.signal_plotters_bpm.connect(self.bpm_update)

    def bpm_update(self, bpm):
        bpm = str(int(round(bpm)))
        self.label_bpm.setText(f'{bpm} BPM')

    def bpm_reset(self):
        self.label_bpm.setText(' BPM')

    # Side Plotter GUI Functions - Only use from main_Script for centralization
    def update_gui_file_selected(self):
        file_selected = self.config_global['extractor']['params']['active_path']
        file_selected = Path(file_selected).name if file_selected else ''
        self.label_currentSource.setText(f'Source: {file_selected}.dat')
