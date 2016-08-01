# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'listen_widget.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class ListenWidgetUI(object):

    def setupUi(self, listen_widget):
        listen_widget.setObjectName("Listen and Record")
        listen_widget.resize(332, 322)
        self.gridLayout = QtWidgets.QGridLayout(listen_widget)
        self.gridLayout.setObjectName("gridLayout")
        self.label_output_device = QtWidgets.QLabel(listen_widget)
        self.label_output_device.setObjectName("label_output_device")
        self.gridLayout.addWidget(self.label_output_device, 7, 0, 1, 3)
        self.button_listen = QtWidgets.QPushButton(listen_widget)
        self.button_listen.setCheckable(False)
        self.button_listen.setObjectName("button_listen")
        self.gridLayout.addWidget(self.button_listen, 0, 0, 1, 1)
        self.button_record_and_stop = QtWidgets.QPushButton(listen_widget)
        self.button_record_and_stop.setEnabled(False)
        self.button_record_and_stop.setCheckable(False)
        self.button_record_and_stop.setObjectName("button_record_and_stop")
        self.gridLayout.addWidget(self.button_record_and_stop, 10, 0, 1, 1)
        self.label_input_device = QtWidgets.QLabel(listen_widget)
        self.label_input_device.setObjectName("label_input_device")
        self.gridLayout.addWidget(self.label_input_device, 1, 0, 1, 1)
        self.time_plot = LongTimePlot(listen_widget)
        self.time_plot.setMinimumSize(QtCore.QSize(300, 100))
        self.time_plot.setObjectName("time_plot")
        self.gridLayout.addWidget(self.time_plot, 11, 0, 1, 3)
        self.radioButton_single_channel = QtWidgets.QRadioButton(listen_widget)
        self.radioButton_single_channel.setChecked(True)
        self.radioButton_single_channel.setObjectName("radioButton_single_channel")
        self.gridLayout.addWidget(self.radioButton_single_channel, 5, 1, 1, 1)
        self.button_clear = QtWidgets.QPushButton(listen_widget)
        self.button_clear.setEnabled(False)
        self.button_clear.setObjectName("button_clear")
        self.gridLayout.addWidget(self.button_clear, 10, 1, 1, 1)
        self.comboBox_input_device = QtWidgets.QComboBox(listen_widget)
        self.comboBox_input_device.setObjectName("comboBox_input_device")
        self.gridLayout.addWidget(self.comboBox_input_device, 3, 0, 1, 3)
        self.comboBox_output_device = QtWidgets.QComboBox(listen_widget)
        self.comboBox_output_device.setObjectName("comboBox_output_device")
        self.gridLayout.addWidget(self.comboBox_output_device, 8, 0, 1, 3)
        self.label_input_channels = QtWidgets.QLabel(listen_widget)
        self.label_input_channels.setObjectName("label_input_channels")
        self.gridLayout.addWidget(self.label_input_channels, 5, 0, 1, 1)
        self.radioButton_dual_channel = QtWidgets.QRadioButton(listen_widget)
        self.radioButton_dual_channel.setObjectName("radioButton_dual_channel")
        self.gridLayout.addWidget(self.radioButton_dual_channel, 5, 2, 1, 1)
        self.button_save = QtWidgets.QPushButton(listen_widget)
        self.button_save.setEnabled(False)
        self.button_save.setObjectName("button_save")
        self.gridLayout.addWidget(self.button_save, 12, 1, 1, 1)
        self.button_playback_and_stop = QtWidgets.QPushButton(listen_widget)
        self.button_playback_and_stop.setEnabled(False)
        self.button_playback_and_stop.setCheckable(False)
        self.button_playback_and_stop.setChecked(False)
        self.button_playback_and_stop.setObjectName("button_playback_and_stop")
        self.gridLayout.addWidget(self.button_playback_and_stop, 12, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 13, 1, 1, 1)

        self.retranslateUi(listen_widget)
        QtCore.QMetaObject.connectSlotsByName(listen_widget)

    def retranslateUi(self, listen_widget):
        _translate = QtCore.QCoreApplication.translate
        listen_widget.setWindowTitle(_translate("listen_widget", "Listen"))
        self.label_output_device.setText(_translate("listen_widget", "Select the output device:"))
        self.button_listen.setToolTip(_translate("listen_widget", "Push to listen to audio input."))
        self.button_listen.setText(_translate("listen_widget", "Listen"))
        self.button_record_and_stop.setToolTip(_translate("listen_widget", "Press to record audio input"))
        self.button_record_and_stop.setText(_translate("listen_widget", "Record"))
        self.label_input_device.setText(_translate("listen_widget", "Select the input device:"))
        self.radioButton_single_channel.setText(_translate("listen_widget", "Single Channel"))
        self.button_clear.setToolTip(_translate("listen_widget", "Press to clear the recorded input"))
        self.button_clear.setText(_translate("listen_widget", "Clear"))
        self.label_input_channels.setText(_translate("listen_widget", "Select input type:"))
        self.radioButton_dual_channel.setText(_translate("listen_widget", "Dual channel"))
        self.button_save.setToolTip(_translate("listen_widget", "Press to save recorded audio"))
        self.button_save.setText(_translate("listen_widget", "Save"))
        self.button_playback_and_stop.setToolTip(_translate("listen_widget", "Press to playback audio recording"))
        self.button_playback_and_stop.setText(_translate("listen_widget", "Play"))

from friture.long_time_plot import LongTimePlot
