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

    def test_input_device(self, device):
        self._logger.push("Testing input device: " + str(device))
        stream = None
        try:
            stream = self._pyaudio.open(format=paInt16,
                                        channels=device.num_input_channels,
                                        rate=SAMPLING_RATE,
                                        input=True,
                                        input_device_index=device.index,
                                        frames_per_buffer=FRAMES_PER_BUFFER)
            stream.start_stream()
            self._logger.push("Success")
            success = True
        except:
            self._logger.push("Fail")
            success = False

        if stream:
            stream.close()

        return success

    def test_output_device(self, device):
        self._logger.push("Testing output device: " + str(device))
        stream = None
        try:
            stream = self._pyaudio.open(format=paInt16,
                                        channels=device.num_input_channels,
                                        rate=SAMPLING_RATE,
                                        output=True,
                                        output_device_index=device.index,
                                        stream_callback=self._test_callback,
                                        frames_per_buffer=FRAMES_PER_BUFFER)
            stream.start_stream()
            self._logger.push("Success")
            success = True
        except:
            self._logger.push("Fail")
            success = False

        if stream:
            stream.close()

        return success

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
        self.logger.push("Device claims %d ms latency" % lat_ms)

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
        self.logger.push("Device claims %d ms latency" % lat_ms)

    def is_input_format_supported(self, device, input_format):
        return self._pyaudio.is_format_supported(SAMPLING_RATE,
                                                 input_device=device,
                                                 input_channels=device.num_input_channels,
                                                 input_format=input_format)

    def is_output_format_supported(self, device, output_format):
        return self._pyaudio.is_format_supported(SAMPLING_RATE,
                                                 output_device=device,
                                                 output_channels=device.num_output_channels,
                                                 output_format=output_format)

    def pause_input_stream(self):
        self.current_input_stream.stop_stream()

    def pause_output_stream(self):
        self.current_output_stream.stop_stream()

    def restart(self):
        self.current_input_stream.start_stream()
        self.current_output_stream.start_stream()

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

    def _test_callback(self, in_data, frame_count, time_info, status_flags):
        pass
