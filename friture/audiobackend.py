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
from pyaudio import PyAudio, paInt16, paInputOverflow
from numpy import ndarray, int16, fromstring, vstack, iinfo, float64
from friture.audio_device_manager import AudioDeviceManager
from friture.audio_stream_manager import AudioStreamManager
# the sample rate below should be dynamic, taken from PyAudio/PortAudio
SAMPLING_RATE = 48000
FRAMES_PER_BUFFER = 512


class AudioBackend(QtCore.QObject):

    IDLE, LISTENING, RECORDING, PLAYING = range(4)

    new_data_available_from_callback = QtCore.pyqtSignal(bytes, int, float, int)
    new_data_available = QtCore.pyqtSignal(ndarray, float, int)

    idle_signal = QtCore.pyqtSignal(int)
    listening_signal = QtCore.pyqtSignal(int)
    recording_signal = QtCore.pyqtSignal(int)
    playing_signal = QtCore.pyqtSignal(int)

    input_device_changed_signal = QtCore.pyqtSignal(bool, int)
    output_device_changed_signal = QtCore.pyqtSignal(bool, int)

    def __init__(self, logger):
        super(AudioBackend, self).__init__()

        self.logger = logger
        self.state = AudioBackend.IDLE

        self.logger.push("Initializing PyAudio")
        self.pa = PyAudio()
        self.pyaudio_terminated = False

        self.device_manager = AudioDeviceManager(self.pa, logger)
        self.stream_manager = AudioStreamManager(self.pa, logger)

        self._initialize_devices()

        self.new_data_available_from_callback.connect(self.handle_new_data)

    def get_readable_input_devices(self):
        return self.device_manager.get_readable_input_devices()

    def get_readable_output_devices(self):
        return self.device_manager.get_readable_output_devices()

    def get_current_input_device_index(self):
        return self.device_manager.get_current_input_device_index()

    def get_current_output_device_index(self):
        return self.device_manager.get_current_output_device_index()

    def set_input_device(self, index):
        device = self.device_manager.get_input_device(index)
        success = self.stream_manager.is_input_format_supported(device, paInt16)

        self.input_device_changed_signal.emit(success,
                                              self.device_manager.get_current_output_device_index())

    def set_output_device(self, index):
        device = self.device_manager.get_output_device(index)
        success = self.stream_manager.is_output_format_supported(device, paInt16)

        self.output_device_changed_signal.emit(success,
                                               self.device_manager.get_current_output_device_index())

    def get_input_stream_time(self):
        return self.stream_manager.get_input_stream_time()

    def get_output_stream_time(self):
        return self.stream_manager.get_output_stream_time()

    def is_input_format_supported(self, device_index, input_format):
        device = self.device_manager.get_input_device(device_index)
        return self.stream_manager.is_input_format_supported(device, input_format)

    def is_output_format_supported(self, device_index, output_format):
        device = self.device_manager.get_output_device(device_index)
        return self.stream_manager.is_output_format_supported(device, output_format)

    def set_input_channels(self, num_channels):
        if num_channels == 1:
            self.device_manager.set_single_channel_input()
        elif num_channels == 2:
            self.device_manager.set_dual_channel_input()

    def select_first_channel(self, index):
        self.device_manager.set_first_input_channel(index)
        success = True
        return success, self.device_manager.get_first_input_channel()

    def select_second_channel(self, index):
        self.device_manager.set_second_input_channel(index)
        success = True
        return success, self.device_manager.get_second_input_channel()

    def get_readable_current_channels(self):
        return self.device_manager.get_input_channels()

    def get_first_input_channel(self):
        return self.device_manager.get_first_input_channel()

    def get_current_second_channel(self):
        return self.device_manager.get_second_input_channel()

    def set_idle(self, previous_widget_state):
        self.state = AudioBackend.IDLE

    def set_listening(self, previous_widget_state):
        self.state = AudioBackend.LISTENING

    def set_recording(self, previous_widget_state):
        self.state = AudioBackend.RECORDING

    def set_playing(self, previous_widget_state):
        self.state = AudioBackend.PLAYING

    def clear_playback_buffer(self):
        pass

    def callback(self, in_data, frame_count, time_info, status):
        # do the minimum from here to prevent overflows, just pass the data to the main thread
        input_time = time_info['input_buffer_adc_time']

        # some API drivers in PortAudio do not return a valid time, so fallback to the current stream time
        if input_time == 0.:
            input_time = time_info['current_time']
        if input_time == 0.:
            input_time = self.get_input_stream_time()

        self.new_data_available_from_callback.emit(in_data, frame_count, input_time, status)

        return None, 0

    def handle_new_data(self, in_data, frame_count, input_time, status):
        if self.pyaudio_terminated:
            return

        if status & paInputOverflow:
            print("Stream overflow!")

        intdata_all_channels = fromstring(in_data, int16)

        int16info = iinfo(int16)
        norm_coeff = max(abs(int16info.min), int16info.max)
        floatdata_all_channels = intdata_all_channels.astype(float64) / float(norm_coeff)

        channel = self.get_current_first_channel()
        nchannels = len(self.device_manager.get_input_channels())
        if self.device_manager.input_is_dual_channel():
            channel_2 = self.get_current_second_channel()

        if len(floatdata_all_channels) != frame_count*nchannels:
            print("Incoming data is not consistent with current channel settings.")
            return

        floatdata1 = floatdata_all_channels[channel::nchannels]

        if self.device_manager.input_is_dual_channel():
            floatdata2 = floatdata_all_channels[channel_2::nchannels]
            floatdata = vstack((floatdata1, floatdata2))
        else:
            floatdata = floatdata1
            floatdata.shape = (1, floatdata.size)

        self.new_data_available.emit(floatdata, input_time, status)

    def pause(self):
        self.stream_manager.pause_input_stream()
        self.stream_manager.pause_output_stream()

    def restart(self):
        self.stream_manager.restart()

    def close(self):
        self.stream_manager.close()

        if not self.pyaudio_terminated:
            # call terminate on PortAudio
            self.logger.push("Terminating PortAudio")
            self.pa.terminate()
            self.logger.push("PortAudio pyaudio_terminated")

            # avoid calling PortAudio methods in the callback/slots
            self.pyaudio_terminated = True

    def _initialize_devices(self):
        for device in self.device_manager.get_input_devices():
            success = self.stream_manager.is_input_format_supported(device, paInt16)
            if not success:
                self.device_manager.remove_input_device(device)
        if self.device_manager.num_input_devices():
            self.device_manager.set_current_input_device(self.device_manager.get_input_device(0))
        else:
            self.logger.push("No valid input devices")

        for device in self.device_manager.get_output_devices():
            success = self.stream_manager.is_output_format_supported(device, paInt16)
            if not success:
                self.device_manager.remove_output_device(device)
        if self.device_manager.num_output_devices():
            self.device_manager.set_current_output_device(self.device_manager.get_output_device(0))
        else:
            self.logger.push("No valid output devices")



