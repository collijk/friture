#!/usr/bin/env python
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

from PyQt5 import QtGui, QtWidgets

class ControlBar(QtWidgets.QWidget):

    def __init__(self, parent):
        super(ControlBar, self).__init__(parent)

        self.setObjectName("Control Bar")

        self.layout = QtWidgets.QHBoxLayout(self)

        self.combobox_select = QtWidgets.QComboBox(self)
        self.combobox_select.setCurrentIndex(0)

        self.layout.addWidget(self.combobox_select)
        self.layout.addStretch()

        self.setLayout(self.layout)

        self.setMaximumHeight(24)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

    def add_widgets(self, widget_names, current_widget_index, tool_tip_message):
        self.combobox_select.addItems(widget_names)
        self.combobox_select.setCurrentIndex(current_widget_index)
        self.combobox_select.setToolTip(tool_tip_message)



class ControlBarWithSettings(ControlBar):

    def __init__(self, parent):
        super().__init__(parent)

        self.settings_button = QtWidgets.QToolButton(self)

        settings_icon = QtGui.QIcon()
        settings_icon.addPixmap(QtGui.QPixmap(":/images-src/dock-settings.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.settings_button.setIcon(settings_icon)

        self.layout.addWidget(self.settings_button)




