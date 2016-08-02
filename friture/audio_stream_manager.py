from PyQt5 import QtCore
from pyaudio import paInt16

SAMPLING_RATE = 48000
FRAMES_PER_BUFFER = 512


class AudioStreamManager(QtCore.QObject):
    """Manager for audio streams."""

    def __init__(self, pyaudio, logger):
        super(AudioStreamManager, self).__init__()

        self._pyaudio = pyaudio
        self._logger = logger
        self._logger.push("Initializing audio stream manager")

        self.current_input_stream = None
        self.current_output_stream = None

    def open_input_stream(self, device, callback):
        if self.current_input_stream is not None:
            self.current_input_stream.close()
        self.current_input_stream = self._pyaudio.open(format=paInt16,
                                                       channels=device.num_input_channels,
                                                       rate=SAMPLING_RATE,
                                                       input=True,
                                                       input_device_index=device.index,
                                                       stream_callback=callback,
                                                       frames_per_buffer=FRAMES_PER_BUFFER)
        self.current_input_stream.start_stream()
        lat_ms = 1000 * self.current_input_stream.get_input_latency()
        self._logger.push("Device claims %d ms latency" % lat_ms)

    def open_output_stream(self, device, callback):
        if self.current_output_stream is not None:
            self.current_output_stream.close()
        self.current_output_stream = self._pyaudio.open(format=paInt16,
                                                        channels=device.num_input_channels,
                                                        rate=SAMPLING_RATE,
                                                        output=True,
                                                        output_device_index=device.index,
                                                        stream_callback=callback,
                                                        frames_per_buffer=FRAMES_PER_BUFFER)
        self.current_output_stream.start_stream()
        lat_ms = 1000 * self.current_output_stream.get_input_latency()
        self._logger.push("Device claims %d ms latency" % lat_ms)

    def is_input_format_supported(self, device, input_format):
        try:
            success = self._pyaudio.is_format_supported(SAMPLING_RATE,
                                                        input_device=device.index,
                                                        input_channels=device.num_input_channels,
                                                        input_format=input_format)
        except ValueError:
            success = False

        return success

    def is_output_format_supported(self, device, output_format):
        try:
            success = self._pyaudio.is_format_supported(SAMPLING_RATE,
                                                        output_device=device.index,
                                                        output_channels=device.num_output_channels,
                                                        output_format=output_format)
        except ValueError:
            success = False

        return success

    def pause_input_stream(self):
        self.current_input_stream.stop_stream()

    def pause_output_stream(self):
        self.current_output_stream.stop_stream()

    def restart(self):
        if self.current_input_stream:
            self.current_input_stream.start_stream()
        if self.current_output_stream:
            self.current_output_stream.start_stream()

    def close(self):
        if self.current_input_stream:
            self.current_input_stream.close()
        if self.current_output_stream:
            self.current_output_stream.close()

    def get_input_stream_time(self):
        try:
            return self.current_input_stream.get_time()
        except OSError:
            return 0

    def get_output_stream_time(self):
        try:
            return self.current_output_stream.get_time()
        except OSError:
            return 0
