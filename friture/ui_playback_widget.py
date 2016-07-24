# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'playback_widget.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class PlaybackWidgetUI(object):
    def setupUi(self, playback_widget):
        playback_widget.setObjectName("playback_widget")
        playback_widget.resize(400, 222)
        self.gridLayout = QtWidgets.QGridLayout(playback_widget)
        self.gridLayout.setObjectName("gridLayout")
        self.label_output_device = QtWidgets.QLabel(playback_widget)
        self.label_output_device.setObjectName("label_output_device")
        self.gridLayout.addWidget(self.label_output_device, 0, 0, 1, 2)
        self.comboBox_output_device = QtWidgets.QComboBox(playback_widget)
        self.comboBox_output_device.setObjectName("comboBox_output_device")
        self.gridLayout.addWidget(self.comboBox_output_device, 1, 0, 1, 2)
        self.button_load = QtWidgets.QPushButton(playback_widget)
        self.button_load.setEnabled(True)
        self.button_load.setCheckable(False)
        self.button_load.setObjectName("button_load")
        self.gridLayout.addWidget(self.button_load, 2, 0, 1, 1)
        self.button_clear = QtWidgets.QPushButton(playback_widget)
        self.button_clear.setEnabled(False)
        self.button_clear.setObjectName("button_clear")
        self.gridLayout.addWidget(self.button_clear, 2, 1, 1, 1)
        self.widget = LongTimePlot(playback_widget)
        self.widget.setMinimumSize(QtCore.QSize(300, 100))
        self.widget.setObjectName("widget")
        self.gridLayout.addWidget(self.widget, 3, 0, 1, 2)
        self.button_playback_and_stop = QtWidgets.QPushButton(playback_widget)
        self.button_playback_and_stop.setEnabled(False)
        self.button_playback_and_stop.setObjectName("button_playback_and_stop")
        self.gridLayout.addWidget(self.button_playback_and_stop, 4, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 2)

        self.retranslateUi(playback_widget)
        QtCore.QMetaObject.connectSlotsByName(playback_widget)

    def retranslateUi(self, playback_widget):
        _translate = QtCore.QCoreApplication.translate
        playback_widget.setWindowTitle(_translate("playback_widget", "Playback"))
        self.label_output_device.setText(_translate("playback_widget", "Select the output device:"))
        self.button_load.setToolTip(_translate("playback_widget", "Press to load an audio file"))
        self.button_load.setText(_translate("playback_widget", "Load"))
        self.button_clear.setToolTip(_translate("playback_widget", "Press to clear the recorded input"))
        self.button_clear.setText(_translate("playback_widget", "Clear"))
        self.button_playback_and_stop.setToolTip(_translate("playback_widget", "Press to playback audio recording"))
        self.button_playback_and_stop.setText(_translate("playback_widget", "Play"))

from friture.long_time_plot import LongTimePlot
