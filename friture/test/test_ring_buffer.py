import unittest
import numpy
from friture.ringbuffer import RingBuffer


class RingBufferTest(unittest.TestCase):

    def setUp(self):
        self.ring_buffer = RingBuffer()
        self.single_channel_data = numpy.random.rand(5000)
        self.dual_channel_data = numpy.random.rand(2, 5000)

    def tearDown(self):
        del self.ring_buffer
        del self.single_channel_data
        del self.dual_channel_data

    def test_buffer_length(self):
        self.fa
        self.assertEqual(self.ring_buffer.buffer_length, 10000, "Buffer length not set to default size.")
        self.assertEqual(2*self.ring_buffer.buffer_length,
                         self.ring_buffer.buffer.shape[1], "Buffer not set to buffer_length")
        self.assertEqual(self.ring_buffer.buffer.shape[1], 20000, "Buffer not set to default size")


if __name__ == "__main__":
    unittest.main()