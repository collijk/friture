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
from friture.controlbar import ControlBar
from friture.logger import PrintLogger
from friture.defaults import DEFAULT_CENTRAL_WIDGET


class AudioIOWidget(QtWidgets.QWidget):

    io_widget_changed = QtCore.pyqtSignal(str)

    def __init__(self, parent=None, logger=PrintLogger()):
        super(AudioIOWidget, self).__init__(parent)
        self.setObjectName("Audio IO Widget")

        self.control_bar = ControlBar(self)
        self.control_bar.combobox_select.currentIndexChanged.connect(self.widget_select)

        self.label = QtWidgets.QLabel(self)
        self.label.setText(" Audio I/O ")  # spaces before and after for nicer alignment
        self.control_bar.layout.insertWidget(0, self.label)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.control_bar)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.logger = logger
        self.io_widgets = None
        self.audio_widget = None

    def set_logger(self, logger):
        self.logger = logger

    def set_io_widgets(self, io_widgets, widget_index):
        [widget.hide() for widget in io_widgets]

        self.io_widgets = io_widgets
        self.audio_widget = io_widgets[widget_index]
        self.io_widget_changed.emit(self.audio_widget.objectName())
        self.audio_widget.show()
        self.layout.addWidget(self.audio_widget)

        widget_names = [widget.objectName() for widget in io_widgets]
        tool_tip_text = "Select the Audio I/O Widget"
        self.control_bar.add_widgets(widget_names, widget_index, tool_tip_text)

    # slot
    def widget_select(self, item):
        self.audio_widget.idle_signal.emit(self.audio_widget.get_state())
        self.audio_widget.hide()
        self.layout.removeWidget(self.audio_widget)
        self.audio_widget.disconnect_all_signals()

        self.audio_widget = self.io_widgets[item]

        self.audio_widget.show()
        self.layout.addWidget(self.audio_widget)
        self.io_widget_changed.emit(self.audio_widget.objectName())

    def canvasUpdate(self):
        if self.audio_widget is not None:
            self.audio_widget.canvas_update()

    def pause(self):
        pass

    def restart(self):
        pass

    # method
    def saveState(self, settings):
        settings.setValue("type", self.io_widgets.index(self.audio_widget))
        self.audio_widget.save_state(settings)

    # method
    def restoreState(self, settings):
        widget_type = settings.value("type", DEFAULT_CENTRAL_WIDGET, type=int)
        self.widget_select(widget_type)
        self.audio_widget.restore_state(settings)
