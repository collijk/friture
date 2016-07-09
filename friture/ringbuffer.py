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

# FIXME problem when self.offset overflows the MAXINT limit !

from numpy import zeros

DEFAULT_BUFFER_LENGTH = 10000
DEFAULT_CHANNELS = 1

class RingBuffer:

    def __init__(self, logger):
        # buffer length is dynamic based on the needs
        self.buffer_length = DEFAULT_BUFFER_LENGTH
        # Begin with a single channel buffer
        self.buffer = zeros((DEFAULT_CHANNELS, 2 * self.buffer_length))
        self.offset = 0
        self.logger = logger

    def push(self, float_data):
        channels = float_data.shape[0]
        data_length = float_data.shape[1]

        # Make sure the buffer and the input data have the same number of channels.
        if channels != self.buffer.shape[0]:
            # Adjust if needed
            self.buffer = zeros((channels, 2 * self.buffer_length))

        self.grow_if_needed(data_length)

        # first copy, always complete
        offset = self.offset % self.buffer_length
        self.buffer[:, offset: offset + data_length] = float_data[:, :]
        # second copy, can be folded
        direct = min(data_length, self.buffer_length - offset)
        folded = data_length - direct
        self.buffer[:, offset + self.buffer_length: offset + self.buffer_length + direct] = float_data[:, 0: direct]
        self.buffer[:, :folded] = float_data[:, direct:]

        self.offset += data_length

    def data(self, length):
        self.grow_if_needed(length)

        stop = self.offset % self.buffer_length + self.buffer_length
        start = stop - length

        while stop > 2 * self.buffer_length:
            self.grow_if_needed(stop)
            stop = self.offset % self.buffer_length + self.buffer_length
            start = stop - length

        if start > 2 * self.buffer_length or start < 0:
            raise ArithmeticError("Start index is wrong %d %d" % (start, self.buffer_length))
        if stop > 2 * self.buffer_length:
            raise ArithmeticError("Stop index is larger than buffer size: %d > %d" % (stop, 2 * self.buffer_length))
        return self.buffer[:, start: stop]

    def data_older(self, length, delay_samples):
        self.grow_if_needed(length + delay_samples)

        start = (self.offset - length - delay_samples) % self.buffer_length + self.buffer_length
        stop = start + length
        return self.buffer[:, start: stop]

    def data_indexed(self, start, length):
        delay = self.offset - start
        self.grow_if_needed(length + delay)

        stop0 = start % self.buffer_length + self.buffer_length
        start0 = stop0 - length

        if start0 > 2 * self.buffer_length or start0 < 0:
            raise ArithmeticError("Start index is wrong %d %d" % (start0, self.buffer_length))
        if stop0 > 2 * self.buffer_length:
            raise ArithmeticError("Stop index is larger than buffer size: %d > %d" % (stop0, 2 * self.buffer_length))

        return self.buffer[:, start0: stop0]

    def grow_if_needed(self, length):
        if length > self.buffer_length:
            # let the buffer grow according to our needs
            old_length = self.buffer_length
            new_length = int(1.5 * length)

            message = "Ringbuffer: growing buffer for length %d" % (new_length)
            if self.logger is not None:
                self.logger.push(message)
            else:
                print(message)

            # create new buffer
            newbuffer = zeros((self.buffer.shape[0], 2 * new_length))
            # copy existing data so that self.offset does not have to be changed
            old_offset_mod = self.offset % old_length
            new_offset_mod = self.offset % new_length
            shift = new_offset_mod - old_offset_mod
            # shift can be negative, computing modulo again
            shift %= new_length
            # first copy, always complete
            newbuffer[:, shift:shift + old_length] = self.buffer[:, :old_length]
            # second copy, can be folded
            direct = min(old_length, new_length - shift)
            folded = old_length - direct
            newbuffer[:, new_length + shift:new_length + shift + direct] = self.buffer[:, :direct]
            newbuffer[:, :folded] = self.buffer[:, direct:direct + folded]
            # assign self.butter to the new larger buffer
            self.buffer = newbuffer
            self.buffer_length = new_length
