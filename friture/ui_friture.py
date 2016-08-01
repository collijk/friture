# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'friture.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(869, 573)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images-src/window-icon.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = AudioIOWidget(MainWindow)
        self.centralwidget.setStyleSheet("")
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setIcon(icon)
        self.actionAbout.setObjectName("actionAbout")
        self.actionNew_dock = QtWidgets.QAction(MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/images-src/new-dock.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionNew_dock.setIcon(icon1)
        self.actionNew_dock.setObjectName("actionNew_dock")
        self.toolBar.addAction(self.actionNew_dock)
        self.toolBar.addAction(self.actionAbout)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Friture"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.actionAbout.setText(_translate("MainWindow", "About Friture"))
        self.actionNew_dock.setText(_translate("MainWindow", "New dock"))
        self.actionNew_dock.setToolTip(_translate("MainWindow", "Add a new dock to Friture window"))

from friture.audio_io_widget import AudioIOWidget
from friture import friture_rc
