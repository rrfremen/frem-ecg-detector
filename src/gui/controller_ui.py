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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QListWidget,
    QListWidgetItem, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(800, 140)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.listWidget_fileSelection = QListWidget(Form)
        self.listWidget_fileSelection.setObjectName(u"listWidget_fileSelection")

        self.verticalLayout_2.addWidget(self.listWidget_fileSelection)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.pushButton_selectFile = QPushButton(Form)
        self.pushButton_selectFile.setObjectName(u"pushButton_selectFile")

        self.horizontalLayout_2.addWidget(self.pushButton_selectFile)

        self.pushButton_selectFolder = QPushButton(Form)
        self.pushButton_selectFolder.setObjectName(u"pushButton_selectFolder")

        self.horizontalLayout_2.addWidget(self.pushButton_selectFolder)

        self.pushButton_clearSelection = QPushButton(Form)
        self.pushButton_clearSelection.setObjectName(u"pushButton_clearSelection")

        self.horizontalLayout_2.addWidget(self.pushButton_clearSelection)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)


        self.horizontalLayout_3.addLayout(self.verticalLayout_2)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pushButton_run = QPushButton(Form)
        self.pushButton_run.setObjectName(u"pushButton_run")

        self.horizontalLayout.addWidget(self.pushButton_run)

        self.pushButton_stop = QPushButton(Form)
        self.pushButton_stop.setObjectName(u"pushButton_stop")

        self.horizontalLayout.addWidget(self.pushButton_stop)

        self.pushButton_settings = QPushButton(Form)
        self.pushButton_settings.setObjectName(u"pushButton_settings")

        self.horizontalLayout.addWidget(self.pushButton_settings)


        self.horizontalLayout_3.addLayout(self.horizontalLayout)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)


        self.gridLayout.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.pushButton_selectFile.setText(QCoreApplication.translate("Form", u"Select File", None))
        self.pushButton_selectFolder.setText(QCoreApplication.translate("Form", u"Select Folder", None))
        self.pushButton_clearSelection.setText(QCoreApplication.translate("Form", u"Clear Selection", None))
        self.pushButton_run.setText(QCoreApplication.translate("Form", u"Run", None))
        self.pushButton_stop.setText(QCoreApplication.translate("Form", u"Stop", None))
        self.pushButton_settings.setText(QCoreApplication.translate("Form", u"Settings", None))
    # retranslateUi

