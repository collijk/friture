# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timoth?Lecomte

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

from PyQt5 import QtWidgets, QtCore
from friture.listen import ListenWidget
from friture.playback import PlaybackWidget
from friture.generator import Generator_Widget
from friture.controlbar import AudioIOControlBar
from friture.logger import PrintLogger
from friture.defaults import DEFAULT_CENTRAL_WIDGET


class AudioIOWidget(QtWidgets.QWidget):

    io_widget_changed = QtCore.pyqtSignal(str)

    def __init__(self, parent, logger=PrintLogger()):
        super(AudioIOWidget, self).__init__(parent)

        self.setObjectName("Audio IO Widget")

        self.control_bar = AudioIOControlBar(self)
        self.control_bar.combobox_select.activated.connect(self.widget_select)

        self.label = QtWidgets.QLabel(self)
        self.label.setText(" Audio I/O ")  # spaces before and after for nicer alignment
        self.control_bar.layout.insertWidget(0, self.label)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.control_bar)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.logger = logger
        self.type = None
        self.audiowidget = None

    # slot
    def widget_select(self, item):
        if self.audiowidget is not None:
            self.audiowidget.close()
            self.audiowidget.deleteLater()

        self.type = item

        if item is 0:
            self.audiowidget = ListenWidget(self, self.logger)
        else:
            self.audiowidget = PlaybackWidget(self, self.logger)
        # TODO: Come back and make the generator widget compatible.
        # elif item is 2:
        #     self.audiowidget = Generator_Widget(self, self.parent().audiobackend, self.logger)

        self.audiowidget.set_buffer(self.parent().audiobuffer)
        self.parent().audiobuffer.new_data_available.connect(self.audiowidget.handle_new_data)

        self.layout.addWidget(self.audiowidget)

        self.control_bar.combobox_select.setCurrentIndex(item)

    def canvasUpdate(self):
        if self.audiowidget is not None:
            self.audiowidget.canvasUpdate()

    def pause(self):
        if self.audiowidget is not None:
            try:
                self.audiowidget.pause()
            except AttributeError:
                pass

    def restart(self):
        if self.audiowidget is not None:
            try:
                self.audiowidget.restart()
            except AttributeError:
                pass


    # method
    def saveState(self, settings):
        settings.setValue("type", self.type)
        self.audiowidget.saveState(settings)

    # method
    def restoreState(self, settings):
        widget_type = settings.value("type", DEFAULT_CENTRAL_WIDGET, type=int)
        self.widget_select(widget_type)
        self.audiowidget.restoreState(settings)
