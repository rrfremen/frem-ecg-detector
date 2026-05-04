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

    signal_gui_file_selected = Signal()
    signal_gui_file_cleared = Signal()
    signal_gui_channel_selected = Signal()
    signal_gui_channel_cleared = Signal()

    signal_live_plot_start = Signal()
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
        self.start_or_is_paused = True

        # self.refresh_rate_init()
        self.preprocessor_init()
        self.detector_init()

    # setup functions
    def setup_signal(self):
        # internal signals
        self.pushButton_addFile.clicked.connect(
            self.select_file
        )
        self.pushButton_removeFile.clicked.connect(
            self.remove_file_selection
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
            self.populate_file_selection()
            self.signal_gui_file_selected.emit()

    def remove_file_selection(self):
        current_item = self.listWidget_fileSelection.currentItem()

        if current_item:
            current_file_path = current_item.text()
            current_row = self.listWidget_fileSelection.currentRow()
            self.listWidget_fileSelection.takeItem(current_row)
            del self.config_global['recordings'][current_file_path]

            # if no files left, clear downstream state
            if self.listWidget_fileSelection.count() == 0:
                self.config_global['extractor']['params']['active_path'] = ''
                self.populate_channel_selection(None)  # type: ignore
                self.signal_gui_file_cleared.emit()
            else:
                self.signal_gui_file_selected.emit()

    def handle_file_selection_changed(self, current, _):
        if current:
            current_path = current.text()
            self.config_global['extractor']['active'] = 'WFDBExtractor'
            self.config_global['extractor']['params']['active_path'] = current_path
            self.config_global['extractor']['fs'] = self.config_global['recordings'][current_path]['fs']

        self.populate_channel_selection(current)

    def handle_channel_selection_changed(self, current, _):
        if not current:
            return
        with self.lock_config_global:
            self.config_global['extractor']['params']['active_channel'] = current.text()
        self.signal_gui_channel_selected.emit()

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

        for current_path in file_paths:
            current_path = current_path[:-4]
            sig_name, fs, units = WFDBExtractor.extract_metadata_from_file(current_path)

            with self.lock_config_global:
                self.config_global['recordings'][current_path] = {
                    'sig_name': sig_name,
                    'fs': fs,
                    'units': units
                }

    def populate_file_selection(self):
        file_paths = list(self.config_global['recordings'].keys())

        current_file_paths = [self.listWidget_fileSelection.item(i).text()
                              for i in range(self.listWidget_fileSelection.count())]
        new_file_paths = [f for f in file_paths if f not in current_file_paths]

        if new_file_paths:
            self.listWidget_fileSelection.addItems(new_file_paths)
            if self.listWidget_fileSelection.currentRow() == -1:
                self.listWidget_fileSelection.setCurrentRow(0)

    def populate_channel_selection(self, current):
        # clear list widget
        self.signal_gui_channel_cleared.emit()
        self.listWidget_channelSelection.clear()
        if not current:
            return
        current_path = current.text()
        channels_avail = self.config_global['recordings'][current_path]['sig_name']
        self.listWidget_channelSelection.addItems(channels_avail)

    # Controller GUI functions - Only use from main_script for centralization
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

    def update_gui_file_cleared(self):
        self.listWidget_fileSelection.setDisabled(True)
        self.label_fileSelection.setDisabled(True)
        self.listWidget_channelSelection.setDisabled(True)
        self.label_channelSelection.setDisabled(True)

    def update_gui_live_plot_started(self):
        self.pushButton_addFile.setDisabled(True)
        self.pushButton_removeFile.setDisabled(True)
        self.listWidget_fileSelection.setDisabled(True)
        self.label_fileSelection.setDisabled(True)
        self.listWidget_channelSelection.setDisabled(True)
        self.label_channelSelection.setDisabled(True)

    def update_gui_live_plot_stopped(self):
        self.pushButton_addFile.setDisabled(False)
        self.pushButton_removeFile.setDisabled(False)
        self.listWidget_fileSelection.setDisabled(False)
        self.label_fileSelection.setDisabled(False)
        self.listWidget_channelSelection.setDisabled(False)
        self.label_channelSelection.setDisabled(False)
