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
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(800, 148)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")

        self.horizontalLayout_3.addLayout(self.verticalLayout_2)

        self.horizontalSpacer = QSpacerItem(21, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.pushButton_selectFile = QPushButton(Form)
        self.pushButton_selectFile.setObjectName(u"pushButton_selectFile")

        self.horizontalLayout_2.addWidget(self.pushButton_selectFile)

        self.pushButton_clearSelection = QPushButton(Form)
        self.pushButton_clearSelection.setObjectName(u"pushButton_clearSelection")

        self.horizontalLayout_2.addWidget(self.pushButton_clearSelection)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

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

        self.horizontalSpacer_2 = QSpacerItem(79, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

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


        self.gridLayout.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.pushButton_selectFile.setText(QCoreApplication.translate("Form", u"Select File", None))
        self.pushButton_clearSelection.setText(QCoreApplication.translate("Form", u"Clear File", None))
        self.pushButton_start.setText(QCoreApplication.translate("Form", u"Start", None))
        self.pushButton_stop.setText(QCoreApplication.translate("Form", u"Stop", None))
        self.pushButton_settings.setText(QCoreApplication.translate("Form", u"Settings", None))
        self.checkBox_showProcessedSignal.setText(QCoreApplication.translate("Form", u"Show Signal Processing", None))
        self.checkBox_showDetector.setText(QCoreApplication.translate("Form", u"Show Detector", None))
        self.checkBox_showAnns.setText(QCoreApplication.translate("Form", u"Show File Annotations", None))
        self.checkBox_darkMode.setText(QCoreApplication.translate("Form", u"Dark Mode", None))
    # retranslateUi

