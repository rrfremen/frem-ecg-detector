# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'controller_ui.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(800, 180)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer = QSpacerItem(21, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.listWidget_fileSelection = QListWidget(Form)
        self.listWidget_fileSelection.setObjectName(u"listWidget_fileSelection")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(2)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.listWidget_fileSelection.sizePolicy().hasHeightForWidth())
        self.listWidget_fileSelection.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.listWidget_fileSelection)

        self.label_fileSelection = QLabel(Form)
        self.label_fileSelection.setObjectName(u"label_fileSelection")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(1)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_fileSelection.sizePolicy().hasHeightForWidth())
        self.label_fileSelection.setSizePolicy(sizePolicy2)

        self.horizontalLayout.addWidget(self.label_fileSelection)


        self.verticalLayout_5.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.pushButton_selectFile = QPushButton(Form)
        self.pushButton_selectFile.setObjectName(u"pushButton_selectFile")

        self.horizontalLayout_2.addWidget(self.pushButton_selectFile)

        self.pushButton_clearSelection = QPushButton(Form)
        self.pushButton_clearSelection.setObjectName(u"pushButton_clearSelection")

        self.horizontalLayout_2.addWidget(self.pushButton_clearSelection)


        self.verticalLayout_5.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.listWidget_channelSelection = QListWidget(Form)
        self.listWidget_channelSelection.setObjectName(u"listWidget_channelSelection")
        sizePolicy1.setHeightForWidth(self.listWidget_channelSelection.sizePolicy().hasHeightForWidth())
        self.listWidget_channelSelection.setSizePolicy(sizePolicy1)

        self.horizontalLayout_5.addWidget(self.listWidget_channelSelection)

        self.label_channelSelection = QLabel(Form)
        self.label_channelSelection.setObjectName(u"label_channelSelection")
        sizePolicy2.setHeightForWidth(self.label_channelSelection.sizePolicy().hasHeightForWidth())
        self.label_channelSelection.setSizePolicy(sizePolicy2)

        self.horizontalLayout_5.addWidget(self.label_channelSelection)


        self.verticalLayout_5.addLayout(self.horizontalLayout_5)


        self.horizontalLayout_3.addLayout(self.verticalLayout_5)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_4)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.pushButton_start = QPushButton(Form)
        self.pushButton_start.setObjectName(u"pushButton_start")

        self.horizontalLayout_4.addWidget(self.pushButton_start)

        self.pushButton_stop = QPushButton(Form)
        self.pushButton_stop.setObjectName(u"pushButton_stop")

        self.horizontalLayout_4.addWidget(self.pushButton_stop)

        self.pushButton_settings = QPushButton(Form)
        self.pushButton_settings.setObjectName(u"pushButton_settings")

        self.horizontalLayout_4.addWidget(self.pushButton_settings)


        self.verticalLayout_3.addLayout(self.horizontalLayout_4)


        self.horizontalLayout_3.addLayout(self.verticalLayout_3)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.checkBox_showProcessedSignal = QCheckBox(Form)
        self.checkBox_showProcessedSignal.setObjectName(u"checkBox_showProcessedSignal")

        self.verticalLayout_4.addWidget(self.checkBox_showProcessedSignal)

        self.checkBox_showDetector = QCheckBox(Form)
        self.checkBox_showDetector.setObjectName(u"checkBox_showDetector")

        self.verticalLayout_4.addWidget(self.checkBox_showDetector)

        self.checkBox_showAnns = QCheckBox(Form)
        self.checkBox_showAnns.setObjectName(u"checkBox_showAnns")

        self.verticalLayout_4.addWidget(self.checkBox_showAnns)

        self.checkBox_darkMode = QCheckBox(Form)
        self.checkBox_darkMode.setObjectName(u"checkBox_darkMode")

        self.verticalLayout_4.addWidget(self.checkBox_darkMode)


        self.horizontalLayout_3.addLayout(self.verticalLayout_4)

        self.horizontalSpacer_3 = QSpacerItem(21, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.horizontalLayout_3.setStretch(0, 1)
        self.horizontalLayout_3.setStretch(1, 4)
        self.horizontalLayout_3.setStretch(2, 1)
        self.horizontalLayout_3.setStretch(3, 1)
        self.horizontalLayout_3.setStretch(4, 1)
        self.horizontalLayout_3.setStretch(5, 1)
        self.horizontalLayout_3.setStretch(6, 1)

        self.gridLayout.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_fileSelection.setText(QCoreApplication.translate("Form", u"File Selection", None))
        self.pushButton_selectFile.setText(QCoreApplication.translate("Form", u"Select File", None))
        self.pushButton_clearSelection.setText(QCoreApplication.translate("Form", u"Clear File", None))
        self.label_channelSelection.setText(QCoreApplication.translate("Form", u"Channel Selection", None))
        self.pushButton_start.setText(QCoreApplication.translate("Form", u"Start", None))
        self.pushButton_stop.setText(QCoreApplication.translate("Form", u"Stop", None))
        self.pushButton_settings.setText(QCoreApplication.translate("Form", u"Settings", None))
        self.checkBox_showProcessedSignal.setText(QCoreApplication.translate("Form", u"Show Signal Processing", None))
        self.checkBox_showDetector.setText(QCoreApplication.translate("Form", u"Show Detector", None))
        self.checkBox_showAnns.setText(QCoreApplication.translate("Form", u"Show File Annotations", None))
        self.checkBox_darkMode.setText(QCoreApplication.translate("Form", u"Dark Mode", None))
    # retranslateUi

