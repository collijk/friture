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

from PyQt5 import QtCore
import numpy as np
from friture.ringbuffer import RingBuffer
from friture.linear_buffer import LinearBuffer

FRAMES_PER_BUFFER = 1024


class AudioBuffer(QtCore.QObject):

    LISTEN, RECORD = 1, 2
    new_data_available = QtCore.pyqtSignal(np.ndarray)

    def __init__(self, logger):
        super().__init__()
        self._logger = logger
        self._live_buffer = RingBuffer(logger)
        self._playback_buffer = LinearBuffer(1, 100*FRAMES_PER_BUFFER)

    def handle_new_data(self, floatdata, data_action):
        self._live_buffer.push(floatdata)
        if data_action == self.RECORD:
            self._playback_buffer.push(floatdata)

        self.new_data_available.emit(floatdata)

