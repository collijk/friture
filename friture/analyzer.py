#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timothée Lecomte

# This file is part of Friture.
#
# Friture is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
#
# Friture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Friture.  If not, see <http://www.gnu.org/licenses/>.

import sys

from PyQt5 import QtCore
# specifically import from PyQt5.QtGui and QWidgets for startup time improvement :
from PyQt5.QtWidgets import QMainWindow, QFileDialog

# importing friture.exceptionhandler also installs a temporary exception hook
from friture.exceptionhandler import errorBox, fileexcepthook
from friture.ui_friture import Ui_MainWindow
from friture.about import About_Dialog  # About dialog

from friture.audiobuffer import AudioBuffer  # audio ring buffer class
from friture.audiobackend import AudioBackend  # audio backend class
from friture.defaults import DEFAULT_CENTRAL_WIDGET
from friture.dockmanager import DockManager


from friture.listen import ListenWidget
from friture.playback import PlaybackWidget
import wave

# the display timer could be made faster when the processing
# power allows it, firing down to every 10 ms
SMOOTH_DISPLAY_TIMER_PERIOD_MS = 10

# the slow timer is used for text refresh
# Text has to be refreshed slowly in order to be readable.
# (and text painting is costly)
SLOW_TIMER_PERIOD_MS = 1000


class Friture(QMainWindow, Ui_MainWindow):

    io_widget_classes = [ListenWidget, PlaybackWidget]

    def __init__(self, logger, parent=None):
        super(Friture, self).__init__(parent)
        self.setupUi(self)

        # exception hook that logs to console, file, and display a message box
        self.errorDialogOpened = False
        sys.excepthook = self.excepthook

        # _logger
        self.logger = logger

        # Initialize the audio data ring buffer
        self.audiobuffer = AudioBuffer(self.logger)

        # Initialize the audio backend
        self.audiobackend = AudioBackend(self.logger)


        # signal containing new data from the audio callback thread, processed as numpy array
        self.audiobackend.new_data_available.connect(self.audiobuffer.handle_new_data)

        # this timer is used to update widgets that just need to display as fast as they can
        self.display_timer = QtCore.QTimer()
        self.display_timer.setInterval(SMOOTH_DISPLAY_TIMER_PERIOD_MS)  # constant timing

        # slow timer
        self.slow_timer = QtCore.QTimer()
        self.slow_timer.setInterval(SLOW_TIMER_PERIOD_MS)  # constant timing

        self.about_dialog = About_Dialog(self, self.logger, self.audiobackend, self.slow_timer)

        self.centralwidget.set_logger(logger)
        self.centralwidget.set_io_widgets(self._get_audio_io_widgets(), DEFAULT_CENTRAL_WIDGET)

        self.dockmanager = DockManager(self, self.logger)

        # timer ticks
        # noinspection PyUnresolvedReferences
        self.display_timer.timeout.connect(self.centralwidget.canvasUpdate)
        # noinspection PyUnresolvedReferences
        self.display_timer.timeout.connect(self.dockmanager.canvasUpdate)

        # toolbar clicks
        self.actionAbout.triggered.connect(self.about_called)
        self.actionNew_dock.triggered.connect(self.dockmanager.new_dock)

        # restore the settings and widgets geometries
        self.restoreAppState()

        # start timers
        self.slow_timer.start()

        self.logger.push("Init finished, entering the main loop")

    # exception hook that logs to console, file, and display a message box
    def excepthook(self, exception_type, exception_value, traceback_object):
        gui_message = fileexcepthook(exception_type, exception_value, traceback_object)

        # we do not want to flood the user with message boxes when the error happens repeatedly on each timer event
        if not self.errorDialogOpened:
            self.errorDialogOpened = True
            errorBox(gui_message)
            self.errorDialogOpened = False

    # slot
    def settings_called(self):
        self.settings_dialog.show()

    def load_file(self):
        pass

    # slot
    def about_called(self):
        self.about_dialog.show()

    # event handler
    def closeEvent(self, event):
        self.audiobackend.close()
        self.saveAppState()
        event.accept()

    # method
    def saveAppState(self):
        settings = QtCore.QSettings("Friture", "Friture")

        settings.beginGroup("Docks")
        self.dockmanager.saveState(settings)
        settings.endGroup()

        settings.beginGroup("CentralWidget")
        self.centralwidget.saveState(settings)
        settings.endGroup()

        settings.beginGroup("MainWindow")
        windowGeometry = self.saveGeometry()
        settings.setValue("windowGeometry", windowGeometry)
        windowState = self.saveState()
        settings.setValue("windowState", windowState)
        settings.endGroup()

    # method
    def restoreAppState(self):
        settings = QtCore.QSettings("Friture", "Friture")

        settings.beginGroup("Docks")
        self.dockmanager.restoreState(settings)
        settings.endGroup()

        settings.beginGroup("CentralWidget")
        self.centralwidget.restoreState(settings)
        settings.endGroup()

        settings.beginGroup("MainWindow")
        # PyCharm thinks there's an argument error here when there's not.
        # noinspection PyArgumentList
        self.restoreGeometry(settings.value("windowGeometry", type=QtCore.QByteArray))
        # noinspection PyArgumentList
        self.restoreState(settings.value("windowState", type=QtCore.QByteArray))
        settings.endGroup()

    # slot
    def timer_on(self):
        if not self.display_timer.isActive():
            self.logger.push("Timer start")
            self.display_timer.start()
            self.centralwidget.restart()
            self.dockmanager.restart()

    def timer_off(self):
        if self.display_timer.isActive():
            self.logger.push("Timer stop")
            self.display_timer.stop()
            self.centralwidget.pause()
            self.dockmanager.pause()

    def _get_audio_io_widgets(self):
        widgets = []
        for widget_class in self.io_widget_classes:
            widget = widget_class(self, self.logger)
            widget.add_input_devices(self.audiobackend.get_readable_input_devices(),
                                     self.audiobackend.get_current_input_device_index())
            widget.add_output_devices(self.audiobackend.get_readable_output_devices(),
                                      self.audiobackend.get_current_output_device_index())
            widgets.append(widget)

        return widgets

    def connect_io_widget(self, io_widget):
        # Connect to the display timer
        io_widget.idle_signal.connect(self.timer_off)
        io_widget.playing_signal.connect(self.timer_on)
        io_widget.listening_signal.connect(self.timer_on)

        # Connect to the audiobackend state
        io_widget.idle_signal.connect(self.audiobackend.set_idle)
        io_widget.listening_signal.connect(self.audiobackend.set_listening)
        io_widget.recording_signal.connect(self.audiobackend.set_recording)
        io_widget.playing_signal.connect(self.audiobackend.set_playing)

        # Connect to file handling
        io_widget.save_data_signal.connect(self.save_data)
        io_widget.load_data_signal.connect(self.load_data)
        io_widget.clear_data_signal.connect(self.audiobackend.clear_playback_buffer)

        # Connect to device management
        io_widget.input_device_change_request_signal.connect(self.audiobackend.set_input_device)
        self.audiobackend.input_device_changed_success_signal.connect(io_widget.change_input_device)
        io_widget.input_channel_number_change_request_signal.connect(self.audiobackend.set_num_input_channels)
        io_widget.output_device_change_request_signal.connect(self.audiobackend.set_output_device)
        self.audiobackend.output_device_changed_success_signal.connect(io_widget.change_output_device)

    def connect_display_widget(self, display_widget):
        self.audiobuffer.new_data_available.connect(display_widget.handle_new_data)

    def save_data(self):
        # PyCharm thinks there are errors here, even though there aren't.
        # noinspection PyTypeChecker,PyCallByClass
        file_name = QFileDialog.getSaveFileName(self, "Save Audio File", "./audio_data", "Wave Files (*.wav)")
        if file_name:
            self.logger.push(file_name)

    def load_data(self):
        # PyCharm thinks there are errors here, even though there aren't.
        # noinspection PyTypeChecker,PyCallByClass
        file_name = QFileDialog.getOpenFileName(self, "Save Audio File", "./audio_data", "Wave Files (*.wav)")

        if file_name:
            pass  # playback_file = wave.open(file_name[1], 'rb')

