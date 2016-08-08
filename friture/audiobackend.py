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
import sounddevice as sound
import numpy

SAMPLING_RATE = 48000
FRAMES_PER_BUFFER = 256  # 512 Causes stream overflows for some reason.


class AudioBackend(QtCore.QObject):
    """Manager for audio input and output.
    
    The :class:`AudioBackend` manages audio devices, streams and audio file i/o.  
    
    Parameters
    ----------
    logger : :class:`friture.logger.Logger`
        The application logger instance.

    Signals
    -------
    
    """

    IDLE, LISTENING, RECORDING, PLAYING = range(4)

    new_data_available = QtCore.pyqtSignal(numpy.ndarray, int)

    input_device_changed_success_signal = QtCore.pyqtSignal(int)
    output_device_changed_success_signal = QtCore.pyqtSignal(int)
    playback_finished_signal = QtCore.pyqtSignal()

    def __init__(self, logger, audio_buffer):
        super().__init__()

        self._logger = logger
        self._audio_buffer = audio_buffer
        self._state = AudioBackend.IDLE

        self._input_devices = [device for device in sound.query_devices() if device['max_input_channels'] > 0]
        self._output_devices = [device for device in sound.query_devices() if device['max_output_channels'] > 0]
        self._input_stream = None
        self._output_stream = None

        self.new_data_available.connect(self._audio_buffer.handle_new_data)

    ###################################################################
    # Methods to get information about the state of the audio system. #
    ###################################################################

    def get_state(self):
        return self._state

    def get_readable_input_devices(self):
        return [device["name"] for device in self._input_devices]

    def get_readable_output_devices(self):
        return [device["name"] for device in self._output_devices]

    def get_current_input_device_index(self):
        return self._input_devices.index(sound.query_devices(device=sound.default.device[0]))

    def get_current_output_device_index(self):
        return self._output_devices.index(sound.query_devices(device=sound.default.device[1]))

    @staticmethod
    def get_readable_current_channels():
        if sound.query_devices(kind='input')['max_input_channels'] == 2:
            return ['L', 'R']
        else:
            return list(range(sound.query_devices(kind='input')['max_input_channels']))

    ########################################################
    # Qt Slots allowing external control over device usage #
    ########################################################

    def set_input_device(self, index):
        """Attempts to set the audio input device.

        Parameters
        ----------
        index : int
            The application's index of the input device

        Notes
        -----
            Emits the `input_device_changed_signal` with the index of the current audio input device.

        """
        if index != self.get_current_input_device_index():
            device = self._input_devices[index]
            try:
                sound.check_input_settings(device=device['name'])
                sound.default.device[0] = device['name']
            except ValueError:
                self._logger.push("Input device not supported")

        self.input_device_changed_success_signal.emit(self.get_current_input_device_index())

    def set_output_device(self, index):
        """Attempts to set the audio output device.

        Parameters
        ----------
        index : int
            The application's index of the output device

        Notes
        -----
            Emits the `output_device_changed_signal` with  the index of the current audio output device.

        """
        if index != self.get_current_output_device_index():
            device = self._output_devices[index]
            try:
                sound.check_output_settings(device=device['name'])
                sound.default.device[1] = device['name']
            except ValueError:
                self._logger.push("Output device not supported")

        self.output_device_changed_success_signal.emit(self.get_current_output_device_index())

    def set_num_input_channels(self, num_channels):
        """Sets the number of input channels

        Parameters
        ----------
        num_channels: int
            The number of channels we want to set the input device to listen on.

        """
        if num_channels == 1:
            sound.default.channels[0] = 1
        elif num_channels == 2:
            sound.default.channels[0] = 2
        else:
            self._logger.push("Invalid number of input channels selected, number of channels unchanged.")

    #################################################
    # Qt slots for setting the audio backend state. #
    #################################################

    def set_idle(self):
        """Pauses any `AudioBackend` activity."""
        
        if self._state == AudioBackend.IDLE:
            pass  # Nothing to do here
        elif self._state == AudioBackend.LISTENING:
            if self._input_stream is not None:
                self._input_stream.stop()
        elif self._state == AudioBackend.RECORDING:
            pass  # Audio buffer will automatically stop recording.
        elif self._state == AudioBackend.PLAYING:
            if self._output_stream is not None and not self._output_stream.stopped:
                self._output_stream.stop()
            self._audio_buffer.reset_playback_position()
            self.playback_finished_signal.emit()
            
        self._state = AudioBackend.IDLE

    def set_listening(self):
        """Starts an input stream with the current recording device."""
        if self._state == AudioBackend.IDLE:
            self._start_listening()
        elif self._state == AudioBackend.LISTENING:
            pass  # Nothing to do here
        elif self._state == AudioBackend.RECORDING:
            pass  # Audio buffer will automatically stop recording.
        elif self._state == AudioBackend.PLAYING:
            if self._output_stream is not None:
                self._output_stream.stop()
            self._start_listening()

        self._state = AudioBackend.LISTENING

    def set_recording(self):
        """Starts writing from an input stream to a data buffer."""
        if self._state == AudioBackend.IDLE:
            self._start_listening()  # Audio buffer will automatically start recording.
        elif self._state == AudioBackend.LISTENING:
            pass  # Audio buffer will automatically start recording.
        elif self._state == AudioBackend.RECORDING:
            pass  # Nothing to do here.
        elif self._state == AudioBackend.PLAYING:
            pass  # Shouldn't ever get here.

        self._state = AudioBackend.RECORDING

    def set_playing(self):
        """Starts playback from a static audio data buffer."""
        if self._state == AudioBackend.IDLE:
            self._start_playing()
        elif self._state == AudioBackend.LISTENING:
            if self._input_stream is not None:
                self._input_stream.stop()
            self._start_playing()
        elif self._state == AudioBackend.RECORDING:
            if self._input_stream is not None:
                self._input_stream.stop()
            self._start_playing()
        elif self._state == AudioBackend.PLAYING:
            pass  # Nothing to do here

        self._state = AudioBackend.PLAYING

    def clear_playback_buffer(self):
        """Clears any data in the playback buffer."""
        self._audio_buffer.clear_playback_data()

    def load_data(self, data, sample_rate):
        data = numpy.transpose(data)

        if sample_rate != SAMPLING_RATE:
            data = self._resample_data(data, sample_rate)

        self._audio_buffer.set_playback_data(data)

    @staticmethod
    def _resample_data(data, sample_rate):
        sampling_ratio = sample_rate / float(SAMPLING_RATE)
        time_original = numpy.linspace(0, data.shape[1], data.shape[1])
        time_resampled = numpy.linspace(0, data.shape[1], sampling_ratio*data.shape[1])

        resampled_data = numpy.empty([data.shape[0], time_resampled.size])
        for channel in numpy.arange(data.shape[0]):
            resampled_data[channel, :] = numpy.interp(time_resampled, time_original, data[channel, :])

        return resampled_data

    def _input_callback(self, in_data, *_):
        in_data = numpy.transpose(in_data).astype(numpy.float64)
        self.new_data_available.emit(in_data, self._state)

    def _output_callback(self, out_data, *_):
        temp_data = self._audio_buffer.pop_playback_data(4*FRAMES_PER_BUFFER)
        if temp_data.shape[1] != 4*FRAMES_PER_BUFFER:
            self.set_idle()
        out_data[:] = numpy.transpose(temp_data)
        self.new_data_available.emit(temp_data.astype(numpy.float64), self._state)

    def close(self):
        if self._input_stream is not None:
            self._input_stream.close()
        if self._output_stream is not None:
            self._output_stream.close()

    def _start_listening(self):
        if self._input_stream is not None:
            self._input_stream.close()

        self._input_stream = sound.InputStream(samplerate=SAMPLING_RATE,
                                               blocksize=FRAMES_PER_BUFFER,
                                               dtype=numpy.float32,
                                               callback=self._input_callback)
        self._input_stream.start()

    def _start_playing(self):
        if self._output_stream is not None:
            self._output_stream.close()

        self._output_stream = sound.OutputStream(samplerate=SAMPLING_RATE,
                                                 blocksize=4*FRAMES_PER_BUFFER,
                                                 channels=2,
                                                 dtype=numpy.float32,
                                                 callback=self._output_callback)
        self._output_stream.start()




