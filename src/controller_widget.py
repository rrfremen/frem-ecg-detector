# internal
import os
import glob
from pathlib import Path

# external
from PySide6.QtWidgets import QWidget, QFileDialog, QStyle
import wfdb

# private
from .gui.controller_ui import Ui_Form
from .parents.thread_manager import ThreadManager


class ControllerWidget(QWidget, ThreadManager, Ui_Form):
    className = 'ControllerWidget'

    def __init__(self, global_config, controller_vars):
        super().__init__()
        self.setupUi(self)
        self.setup_ui_local()
        self.setup_signal(controller_vars)

        # shared variables
        self.config_global = global_config

        # local variables
        self.error_txt = ''
        self.is_paused = False

    # setup functions
    def setup_signal(self, controller_vars):
        # internal signals
        self.pushButton_selectFile.clicked.connect(
            self.select_file
        )
        self.pushButton_selectFolder.clicked.connect(
            self.select_folder
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

        # external signals
        self.lock_config_global = controller_vars['lock_config_global']
        self.signal_display_recs = controller_vars['display_recs']
        self.signal_live_plot_start = controller_vars['signal_live_plot_start']
        self.signal_live_plot_pause = controller_vars['signal_live_plot_pause']
        self.signal_live_plot_continue = controller_vars['signal_live_plot_continue']
        self.signal_live_plot_stop = controller_vars['signal_live_plot_stop']

    def setup_ui_local(self):
        self.pushButton_selectFolder.setDisabled(True)
        # switch button texts to symbols
        self.pushButton_start.setText('')
        self.pushButton_start.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.pushButton_stop.setText('')
        self.pushButton_stop.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        # grey out buttons first
        self.pushButton_start.setDisabled(True)
        self.pushButton_stop.setDisabled(True)
        self.pushButton_settings.setDisabled(True)

    # button functions
    def select_file(self):
        selected_files = QFileDialog.getOpenFileNames(
            self,
            caption='Select one or more files to open',
            dir='/',
            filter='*.dat'
        )

        if selected_files:
            self.thread_add_worker(self.tw_check_selected_files, file_paths=selected_files[0])

    def select_folder(self):
        selected_folder = QFileDialog.getExistingDirectory(
            self,
            caption='Select a folder to open',
            dir='/'
        )

        if selected_folder:
            self.thread_add_worker(self.tw_check_selected_files, file_paths=selected_folder)

    def clear_recs_selection(self):
        pass

    def live_plot_start(self):
        if not self.is_paused:
            self.signal_live_plot_start.emit()
            self.pushButton_start.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
            self.is_paused = True
        else:
            self.signal_live_plot_pause.emit()
            self.pushButton_start.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            self.is_paused = False

    def live_plot_stop(self):
        self.signal_live_plot_stop.emit()
        self.pushButton_start.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    # thread worker functions
    def tw_check_selected_files(self, file_paths):
        if type(file_paths) is str:  # folder
            file_paths = glob.glob(os.path.join(file_paths, '*.dat'))
            if not file_paths:
                raise ValueError('No recording was found in the selected folder')

        # check whether header file exists for the selected files
        final_file_paths = []
        relevant_headers = None
        for current_path in file_paths:
            current_path = current_path[:-4]
            if Path(current_path + '.hea').exists():  # faster to extract header only
                current_header = wfdb.rdheader(current_path)
            else:
                current_header = wfdb.rdrecord(current_path)
            if relevant_headers is None:  # get reference for the files
                relevant_headers = [
                    current_header.sig_name,
                    current_header.fs,
                    current_header.units,
                    current_header.samps_per_frame
                ]
                # insist on MLII for now
                if len(self.config_global['recordings']['channels_in_use']) == 1:
                    if self.config_global['recordings']['channels_in_use'][0] == 'MLII':
                        if 'MLII' in current_header.sig_name:
                            final_file_paths.append(current_path)
                        else:
                            break
            else:  # compare all headers to the first header
                current_relevant_headers = [
                    current_header.sig_name,
                    current_header.fs,
                    current_header.samps_per_frame,
                    current_header.units
                ]
                for i in range(len(relevant_headers)):
                    if relevant_headers[i] != current_relevant_headers[i]:
                        break
                final_file_paths.append(current_path)

        # update config - recordings
        with self.lock_config_global:
            self.config_global['recordings'].update({
                'paths': final_file_paths,
                'sig_name': relevant_headers[0],
                'fs': relevant_headers[1],
                'units': relevant_headers[2],
            })

        self.signal_display_recs.emit()

    # Controller GUI functions - Only use from main_script for centralization
    def update_gui_file_selection(self):
        self.listWidget_fileSelection.addItems(self.config_global['recordings']['paths'])
        self.pushButton_start.setDisabled(False)
        self.pushButton_stop.setDisabled(False)
        self.pushButton_settings.setDisabled(False)
