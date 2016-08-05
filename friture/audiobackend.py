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
from friture.audio_stream_manager import AudioStreamManager, SAMPLING_RATE, FRAMES_PER_BUFFER


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

    new_data_available_from_callback = QtCore.pyqtSignal(bytes, int, float, int)
    new_data_available = QtCore.pyqtSignal(ndarray, int)

    input_device_changed_success_signal = QtCore.pyqtSignal(int)
    output_device_changed_success_signal = QtCore.pyqtSignal(int)

    def __init__(self, logger):
        super().__init__()

        self.input_format = paInt16

        self._logger = logger
        self._state = AudioBackend.IDLE

        self._logger.push("Initializing PyAudio")
        self._pyaudio = PyAudio()
        self._pyaudio_terminated = False

        self._device_manager = AudioDeviceManager(self._pyaudio, logger)
        self._stream_manager = AudioStreamManager(self._pyaudio, logger)

        self._initialize_devices()

        self.new_data_available_from_callback.connect(self.handle_new_data)

    ###################################################################
    # Methods to get information about the state of the audio system. #
    ###################################################################

    def get_state(self):
        return self._state

    def get_readable_input_devices(self):
        return self._device_manager.get_readable_input_devices()

    def get_readable_output_devices(self):
        return self._device_manager.get_readable_output_devices()

    def get_current_input_device_index(self):
        return self._device_manager.get_current_input_device_index()

    def get_current_output_device_index(self):
        return self._device_manager.get_current_output_device_index()

    def get_input_stream_time(self):
        return self._stream_manager.get_input_stream_time()

    def get_output_stream_time(self):
        return self._stream_manager.get_output_stream_time()

    def get_readable_current_channels(self):
        return self._device_manager.get_input_channels()

    def get_first_input_channel(self):
        return self._device_manager.get_first_input_channel()

    def get_current_second_channel(self):
        return self._device_manager.get_second_input_channel()

    ########################################################
    # Qt Slots allowing external control over device usage #
    ########################################################

    def set_input_device(self, index):
        """Attempts to set the audio input device.

        Parameters
        ----------
        index : int
            The application's index of the input device (as opposed to the pyaudio index)

        Notes
        -----
            Emits the `input_device_changed_signal` with the success status and the index
            of the current audio input device.

        """
        if index != self._device_manager.get_current_input_device_index():
            device = self._device_manager.get_input_device(index)
            success = self._stream_manager.is_input_format_supported(device, self.input_format)
            if success:
                self._device_manager.set_current_input_device(device)
                self._stream_manager.clear_input_stream()
        else:
            success = True

        self.input_device_changed_success_signal.emit(self._device_manager.get_current_input_device_index())

    def set_output_device(self, index):
        """Attempts to set the audio output device.

        Parameters
        ----------
        index : int
            The application's index of the output device (as opposed to the pyaudio index)

        Notes
        -----
            Emits the `output_device_changed_signal` with the success status and the index
            of the current audio output device.

        """
        if index != self._device_manager.get_current_output_device_index():
            device = self._device_manager.get_output_device(index)
            success = self._stream_manager.is_output_format_supported(device, paInt16)
            if success:
                self._device_manager.set_current_output_device(device)
                self._stream_manager.clear_output_stream()
        else:
            success = True

        self.output_device_changed_success_signal.emit(self._device_manager.get_current_output_device_index())

    def set_num_input_channels(self, num_channels):
        """Sets the number of input channels

        Parameters
        ----------
        num_channels: int
            The number of channels we want to set the input device to listen on.

        """
        if num_channels == 1:
            self._device_manager.set_single_channel_input()
        elif num_channels == 2:
            self._device_manager.set_dual_channel_input()
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
            self._stream_manager.pause_input_stream()
        elif self._state == AudioBackend.RECORDING:
            pass  # Pause the recording steam.
        elif self._state == AudioBackend.PLAYING:
            pass  # Pause the output stream.
            
        self._state = AudioBackend.IDLE

    def set_listening(self):
        """Starts an input stream with the current recording device."""
        if self._state == AudioBackend.IDLE:
            if self._stream_manager.input_stream_is_open():
                self._stream_manager.restart_input_stream()
            else:
                device = self._device_manager.get_current_input_device()
                self._stream_manager.open_input_stream(device, self.callback)
        elif self._state == AudioBackend.LISTENING:
            pass # Nothing to do here
        elif self._state == AudioBackend.RECORDING:
            pass
        elif self._state == AudioBackend.PLAYING:
            pass

        self._state = AudioBackend.LISTENING

    def set_recording(self):
        """Starts writing from an input stream to a data buffer."""
        if self._state == AudioBackend.IDLE:
            pass  # Open up a recording stream and buffer.
        elif self._state == AudioBackend.LISTENING:
            pass  # Open up a recording stream and buffer.
        elif self._state == AudioBackend.RECORDING:
            pass  # Nothing to do here.
        elif self._state == AudioBackend.PLAYING:
            pass  # Shouldn't ever get here.
        self._state = AudioBackend.RECORDING

    def set_playing(self):
        """Starts playback from a static audio data buffer."""
        # Check we have data available.
        if self._state == AudioBackend.IDLE:
            pass  # Open an output stream if not one already.  Start reading from the stream.
        elif self._state == AudioBackend.LISTENING:
            pass  # Stop the input stream, Open the output steam if not one already.  Start reading from the stream.
        elif self._state == AudioBackend.RECORDING:
            pass  # Shouldn't be able to get here.
        elif self._state == AudioBackend.PLAYING:
            pass  # Nothing to do here

        self._state = AudioBackend.PLAYING

    def clear_playback_buffer(self):
        """Clears any data in the playback buffer."""
        if self._state == AudioBackend.IDLE:
            pass  # Clear the data.
        elif self._state == AudioBackend.LISTENING:
            pass  # Clear the data.
        elif self._state == AudioBackend.RECORDING:
            pass  # Clear the data without interrupting the write/display
        elif self._state == AudioBackend.PLAYING:
            pass  # Shouldn't be able to get here.

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
        if self._pyaudio_terminated:
            return

        if status & paInputOverflow:
            print("Stream overflow!")

        intdata_all_channels = fromstring(in_data, int16)

        int16info = iinfo(int16)
        norm_coeff = max(abs(int16info.min), int16info.max)
        floatdata_all_channels = intdata_all_channels.astype(float64) / float(norm_coeff)

        channel = self._device_manager.get_first_input_channel()
        nchannels = len(self._device_manager.get_input_channels())

        if len(floatdata_all_channels) != frame_count*nchannels:
            print("Incoming data is not consistent with current channel settings.")
            return

        floatdata1 = floatdata_all_channels[channel::nchannels]

        if self._device_manager.input_is_dual_channel():
            channel_2 = self._device_manager.get_second_input_channel()
            floatdata2 = floatdata_all_channels[channel_2::nchannels]
            floatdata = vstack((floatdata1, floatdata2))
        else:
            floatdata = floatdata1
            floatdata.shape = (1, floatdata.size)

        self.new_data_available.emit(floatdata, self._state)

    def restart(self):
        self._stream_manager.restart()

    def close(self):
        self._stream_manager.close()

        if not self._pyaudio_terminated:
            # call terminate on PortAudio
            self._logger.push("Terminating PortAudio")
            self._pyaudio.terminate()
            self._logger.push("PortAudio pyaudio_terminated")

            # avoid calling PortAudio methods in the callback/slots
            self._pyaudio_terminated = True

    def _initialize_devices(self):
        for device in self._device_manager.get_input_devices():
            # FIXME:
            # Occasionally throws a non-critical error  on linux due to bugs in portaudio/alsa.
            # Nothing we can do about it for now.  Similar bugs occur in audacity.
            # Causes a failure to open an input device.  Right now this is handled by reverting
            # to the system default and allowing the user to try again. Needs further research.
            success = self._stream_manager.is_input_format_supported(device, paInt16)
            if not success:
                pass
        if self._device_manager.num_input_devices():
            self._device_manager.set_current_input_device(self._device_manager.get_input_device(0))
        else:
            self._logger.push("No valid input devices")

        for device in self._device_manager.get_output_devices():
            success = self._stream_manager.is_output_format_supported(device, paInt16)
            if not success:
                self._device_manager.remove_output_device(device)
        if self._device_manager.num_output_devices():
            self._device_manager.set_current_output_device(self._device_manager.get_output_device(0))
        else:
            self._logger.push("No valid output devices")



