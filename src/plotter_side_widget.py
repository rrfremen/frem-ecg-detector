# external
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QGuiApplication

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

        self.refresh_rate_init()

    def setup_signal(self, plotter_side_vars):
        # internal signal
        self.comboBox_refreshRate.currentIndexChanged.connect(self.refresh_rate_update)

        # external signal
        self.lock_config_global = plotter_side_vars['lock_config_global']
        self.signal_refresh_rate_update = plotter_side_vars['signal_refresh_rate_update']

    def refresh_rate_init(self):
        current_disp_refresh_rate = int(QGuiApplication.primaryScreen().refreshRate())
        refresh_rates = []
        if current_disp_refresh_rate >= 30:
            refresh_rates.extend([30, 20, 10])
        else:
            refresh_rates.append(current_disp_refresh_rate)

        self.comboBox_refreshRate.addItems([str(r) + ' Hz' for r in refresh_rates])
        if 20 in refresh_rates:
            index = refresh_rates.index(20)
            self.comboBox_refreshRate.setCurrentIndex(index)

        with self.lock_config_global:
            self.config_global['plotter']['display']['refresh_rate'] = int(self.comboBox_refreshRate.currentText()[:-3])

    def refresh_rate_update(self):
        with self.lock_config_global:
            self.config_global['plotter']['display']['refresh_rate'] = int(self.comboBox_refreshRate.currentText()[:-3])
        self.signal_refresh_rate_update.emit()
