# built-in
import os
import glob

# external
from PySide6.QtWidgets import QWidget, QFileDialog, QStyle
from PySide6.QtCore import Signal

# internal
from .gui.controller_ui import Ui_Form
from .algorithms.extractor.extractor_WFDB import WFDBExtractor


class ControllerWidget(QWidget, Ui_Form):
    className = 'ControllerWidget'

    signal_display_recs = Signal()

    signal_live_plot_start = Signal()
    signal_live_plot_start_timer = Signal()
    signal_live_plot_pause = Signal()
    signal_live_plot_stop = Signal()
    signal_plot_lower_processed = Signal()
    signal_plot_lower_detector = Signal()
    signal_app_dark_mode = Signal()

    def __init__(self, global_config, lock_config):
        super().__init__()
        self.setupUi(self)
        self.setup_ui_local()
        self.setup_signal()

        # shared variables
        self.config_global = global_config
        self.lock_config_global = lock_config

        # local variables
        self.error_txt = ''
        self.start_or_is_paused = True

        # self.refresh_rate_init()
        self.preprocessor_init()
        self.detector_init()

    # setup functions
    def setup_signal(self):
        # internal signals
        self.pushButton_selectFile.clicked.connect(
            self.select_file
        )
        self.pushButton_clearSelection.clicked.connect(
            self.clear_recs_selection
        )
        self.pushButton_start.clicked.connect(
            self.live_plot_start
        )
        self.pushButton_stop.clicked.connect(
            self.live_plot_stop
        )
        self.checkBox_showProcessedSignal.clicked.connect(
            self.plot_lower_processed_toggle
        )
        self.checkBox_showDetector.clicked.connect(
            self.plot_lower_detector_toggle
        )
        self.checkBox_darkMode.clicked.connect(
            lambda: self.signal_app_dark_mode.emit()
        )
        self.listWidget_fileSelection.currentItemChanged.connect(
            self.handle_file_selection_changed
        )
        self.listWidget_channelSelection.currentItemChanged.connect(
            self.handle_channel_selection_changed
        )

    def setup_ui_local(self):
        # switch button texts to symbols
        self.pushButton_start.setText('')
        self.pushButton_start.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.pushButton_stop.setText('')
        self.pushButton_stop.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        # grey out stuff
        self.pushButton_start.setDisabled(True)
        self.pushButton_stop.setDisabled(True)
        self.pushButton_settings.setDisabled(True)
        self.checkBox_showProcessedSignal.setDisabled(True)
        self.checkBox_showDetector.setDisabled(True)
        self.checkBox_showAnns.setDisabled(True)
        self.listWidget_fileSelection.setDisabled(True)
        self.label_fileSelection.setDisabled(True)
        self.listWidget_channelSelection.setDisabled(True)
        self.label_channelSelection.setDisabled(True)

    def preprocessor_init(self):
        # TODO - waiting UI update
        self.config_global['preprocessor']['active'] = 'DefaultPreprocessor'

    def detector_init(self):
        # TODO - waiting UI update
        self.config_global['detector']['active'] = 'DefaultDetector'

    # UI functions
    def select_file(self):
        selected_files = QFileDialog.getOpenFileNames(
            self,
            caption='Select one or more files to open',
            dir='/',
            filter='*.dat'
        )

        if selected_files[0]:
            self.check_selected_files(selected_files[0])

    def clear_recs_selection(self):
        pass

    def plot_lower_processed_toggle(self):
        self.signal_plot_lower_processed.emit()
        if self.checkBox_showDetector.isChecked() and not self.checkBox_showProcessedSignal.isChecked():
            self.checkBox_showDetector.setChecked(False)

    def plot_lower_detector_toggle(self):
        self.signal_plot_lower_detector.emit()
        if not self.checkBox_showProcessedSignal.isChecked():
            self.checkBox_showProcessedSignal.setChecked(True)

    def live_plot_start(self):
        if self.start_or_is_paused:
            self.signal_live_plot_start.emit()
            self.pushButton_start.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
            self.start_or_is_paused = False
        else:
            self.signal_live_plot_pause.emit()
            self.pushButton_start.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            self.start_or_is_paused = True

    def live_plot_stop(self):
        self.signal_live_plot_stop.emit()
        self.pushButton_start.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    # internal functions
    def check_selected_files(self, file_paths):
        if type(file_paths) is str:  # folder
            file_paths = glob.glob(os.path.join(file_paths, '*.dat'))
            if not file_paths:
                raise ValueError('No recording was found in the selected folder')

        # TODO - allow multiple files
        file_limit = 1

        for i, current_path in enumerate(file_paths):
            if i < file_limit:
                current_path = current_path[:-4]
                sig_name, fs, units = WFDBExtractor.extract_metadata_from_file(current_path)

                with self.lock_config_global:
                    self.config_global['recordings'][current_path] = {
                        'sig_name': sig_name,
                        'fs': fs,
                        'units': units
                    }

        self.populate_file_selection()

    def populate_file_selection(self):
        # clear list widget
        self.listWidget_fileSelection.clear()

        # populate list widget for file selection and select the first one
        file_paths = list(self.config_global['recordings'].keys())
        self.listWidget_fileSelection.addItems(file_paths)
        self.listWidget_fileSelection.setCurrentRow(0)

        self.update_gui_file_selected()

    def populate_channel_selection(self, current_path):
        # clear list widget
        self.listWidget_channelSelection.clear()
        channels_avail = self.config_global['recordings'][current_path]['sig_name']
        self.listWidget_channelSelection.addItems(channels_avail)

    def handle_file_selection_changed(self, current, _):
        current_path = current.text()
        self.config_global['extractor']['active'] = 'WFDBExtractor'
        self.config_global['extractor']['params']['active_path'] = current_path
        self.config_global['extractor']['fs'] = self.config_global['recordings'][current_path]['fs']

        self.populate_channel_selection(current_path)

    def handle_channel_selection_changed(self, current, _):
        with self.lock_config_global:
            self.config_global['extractor']['params']['active_channel'] = current.text()
        self.signal_display_recs.emit()

    # Controller GUI functions
    def update_gui_file_selected(self):
        self.listWidget_fileSelection.setDisabled(False)
        self.label_fileSelection.setDisabled(False)
        self.listWidget_channelSelection.setDisabled(False)
        self.label_channelSelection.setDisabled(False)

    def update_gui_channel_selected(self):
        self.pushButton_start.setDisabled(False)
        self.pushButton_stop.setDisabled(False)
        self.pushButton_settings.setDisabled(False)
        self.checkBox_showProcessedSignal.setDisabled(False)
        self.checkBox_showDetector.setDisabled(False)

    def update_gui_no_file_selected(self):
        pass

    def update_gui_no_channel_selected(self):
        pass

    def update_gui_live_plot_started(self):
        pass

    def update_gui_live_plot_stopped(self):
        pass
