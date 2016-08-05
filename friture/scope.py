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

from PyQt5 import QtWidgets
import numpy
from friture.timeplot import TimePlot
from friture.audiobackend import SAMPLING_RATE
from friture.logger import PrintLogger
from friture.ring_buffer import RingBuffer

SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25
DEFAULT_TIMERANGE = 2 * SMOOTH_DISPLAY_TIMER_PERIOD_MS


class Scope_Widget(QtWidgets.QWidget):

    name = "Oscilloscope"

    def __init__(self, parent, logger=PrintLogger()):
        super().__init__(parent)

        self.logger = logger

        self.setObjectName(self.name)
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.PlotZoneUp = TimePlot(self, self.logger)
        self.PlotZoneUp.setObjectName("PlotZoneUp")
        self.gridLayout.addWidget(self.PlotZoneUp, 0, 0, 1, 1)

        self.settings_dialog = Scope_Settings_Dialog(self, self.logger)

        self.time_range_s = DEFAULT_TIMERANGE * 0.001
        self.num_sample_points = int(self.time_range_s * SAMPLING_RATE)

        self.time = numpy.linspace(0, self.time_range_s, self.num_sample_points)
        # Keep a small display buffer so we can use triggering in the data display.
        self.display_buffer = RingBuffer(1, 2*self.num_sample_points)

    def handle_new_data(self, floatdata):
        self.display_buffer.push(floatdata)

        data = self.display_buffer.unwound_data()
        is_dual_channel = data.shape[0] == 2

        # trigger on the first channel only
        trigger_data = data[0, :]
        # trigger on half of the waveform
        half_sample = int(self.num_sample_points/2)
        trig_search_start = half_sample
        trig_search_stop = -half_sample
        trigger_data = trigger_data[trig_search_start:trig_search_stop]

        trigger_level = data.max() * 2. / 3.
        trigger_pos = numpy.where((trigger_data[:-1] < trigger_level) * (trigger_data[1:] >= trigger_level))[0]

        if len(trigger_pos) > 0:
            shift = trigger_pos[0]
        else:
            return

        shift += trig_search_start
        data = data[:, shift - half_sample: shift + half_sample]

        y = data[0, :]
        if is_dual_channel:
            y2 = data[1, :]
        else:
            y2 = None

        dBscope = False
        if dBscope:
            dBmin = -50.
            y = numpy.sign(y) * (20 * numpy.log10(
                abs(y))).clip(dBmin, 0.) / (-dBmin) + numpy.sign(y) * 1.
            if is_dual_channel:
                y2 = numpy.sign(y2) * (20 * numpy.log10(
                    abs(y2))).clip(dBmin, 0.) / (-dBmin) + numpy.sign(y2) * 1.
            else:
                y2 = None

        if y2 is not None:
            self.PlotZoneUp.setdataTwoChannels(self.time, y, y2)
        else:
            self.PlotZoneUp.setdata(self.time, y)

    # method
    def canvasUpdate(self):
        return

    def pause(self):
        self.PlotZoneUp.pause()

    def restart(self):
        self.PlotZoneUp.restart()

    # slot
    def set_timerange(self, timerange):
        self.time_range_s = timerange*0.001
        self.num_sample_points = int(self.time_range_s * SAMPLING_RATE)
        self.time = numpy.linspace(0, self.time_range_s, self.num_sample_points)
        self.display_buffer.reset(self.display_buffer.num_channels, self.num_sample_points)

    # slot
    def settings_called(self, checked):
        self.settings_dialog.show()

    # method
    def saveState(self, settings):
        self.settings_dialog.saveState(settings)

    # method
    def restoreState(self, settings):
        self.settings_dialog.restoreState(settings)


class Scope_Settings_Dialog(QtWidgets.QDialog):

    def __init__(self, parent, logger):
        super().__init__(parent)

        self.logger = logger

        self.setWindowTitle("Scope settings")

        self.formLayout = QtWidgets.QFormLayout(self)

        self.doubleSpinBox_timerange = QtWidgets.QDoubleSpinBox(self)
        self.doubleSpinBox_timerange.setDecimals(1)
        self.doubleSpinBox_timerange.setMinimum(0.1)
        self.doubleSpinBox_timerange.setMaximum(1000.0)
        self.doubleSpinBox_timerange.setProperty("value", DEFAULT_TIMERANGE)
        self.doubleSpinBox_timerange.setObjectName("doubleSpinBox_timerange")
        self.doubleSpinBox_timerange.setSuffix(" ms")

        self.formLayout.addRow("Time range:", self.doubleSpinBox_timerange)

        self.setLayout(self.formLayout)

        self.doubleSpinBox_timerange.valueChanged.connect(self.parent().set_timerange)

    # method
    def saveState(self, settings):
        settings.setValue("timeRange", self.doubleSpinBox_timerange.value())

    # method
    def restoreState(self, settings):
        timeRange = settings.value("timeRange", DEFAULT_TIMERANGE, type=float)
        self.doubleSpinBox_timerange.setValue(timeRange)
