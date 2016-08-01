import unittest
from pyaudio import PyAudio
from friture.logger import Logger
from friture.audio_device_manager import AudioDeviceManager
from friture.audio_stream_manager import AudioStreamManager


class AudioStreamManagerTest(unittest.TestCase):
    def setUp(self):
        pyaudio = PyAudio()
        logger = Logger()
        self.device_manager = AudioDeviceManager(pyaudio, logger)
        self.stream_manager = AudioStreamManager(pyaudio, logger)

    def tearDown(self):
        pass

    def test_creation(self):
        pass

    def test_test_input_device(self):
        for device in self.device_manager.get_input_devices():
            print(device)
            success = self.stream_manager.test_input_device(device)
            print(success)

    def test_test_output_device(self):
        for device in self.device_manager.get_output_devices():
            print(device)
            success = self.stream_manager.test_output_device(device)
            print(success)


if __name__ == "__main__":
    unittest.main()