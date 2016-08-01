import unittest
from pyaudio import PyAudio
from friture.logger import Logger
from friture.audio_device_manager import AudioDeviceManager


class AudioDeviceManagerTest(unittest.TestCase):

    def setUp(self):
        pyaudio = PyAudio()
        logger = Logger()
        self.device_manager = AudioDeviceManager(pyaudio, logger)

    def tearDown(self):
        pass

    def test_creation(self):
        pass


if __name__ == "__main__":
    unittest.main()
