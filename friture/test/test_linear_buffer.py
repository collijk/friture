import unittest
import numpy
from friture.linear_buffer import LinearBuffer


class LinearBufferTest(unittest.TestCase):

    def setUp(self):
        self.a = LinearBuffer(1, 5)
        self.b = numpy.arange(3).reshape([1, 3])
        self.c = numpy.arange(7).reshape([1, 7])
        self.d = numpy.arange(10).reshape([5, 2])
        self.e = numpy.arange(10).reshape([1,10])

    def test_buffer_initialization(self):
        self.assertEqual(1, self.a.num_channels, self.a.data)
        self.assertEqual(5, self.a.length, self.a.data)
        self.assertEqual(0, self.a.num_unread_data_points(), self.a.data)
        self.assertTrue(numpy.array_equal(self.a.data, numpy.zeros([1, 5])), self.a.data)
        self.assertEqual(self.a.write_position, 0, self.a.data)
        self.assertEqual(self.a.read_position, 0, self.a.data)

    def test_push(self):
        self.a.push(self.b)
        self.assertEqual(1, self.a.num_channels, self.a.data)
        self.assertEqual(5, self.a.length, self.a.data)
        self.assertEqual(3, self.a.num_unread_data_points(), self.a.data)
        self.assertTrue(numpy.array_equal(self.a.data, numpy.array([[0., 1., 2., 0., 0.]])), self.a.data)
        self.assertEqual(self.a.write_position, 3, self.a.data)
        self.assertEqual(self.a.read_position, 0, self.a.data)

    def test_multi_push_with_grow(self):
        self.a.push(self.b)
        self.a.push(self.b)
        self.assertEqual(1, self.a.num_channels, self.a.data)
        self.assertEqual(10, self.a.length, self.a.data)
        self.assertEqual(6, self.a.num_unread_data_points(), self.a.data)
        self.assertTrue(numpy.array_equal(self.a.data, numpy.array([
            [0., 1., 2., 0., 1., 2., 0., 0., 0., 0.]])), self.a.data)
        self.assertEqual(self.a.write_position, 6, self.a.data)
        self.assertEqual(self.a.read_position, 0, self.a.data)

    def test_multi_push_into_big(self):
        pass

    def test_push_big(self):
        pass

    def test_push_multi_channel_small(self):
        pass

    def test_push_channel_number_change(self):
        pass

    def test_multi_push_multi_channel(self):
        pass

    def test_pop_single(self):
        pass

    def test_pop_multi(self):
        pass

if __name__ == "__main__":
    unittest.main()