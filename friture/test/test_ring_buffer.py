import unittest
import numpy
from friture.ring_buffer import RingBuffer


class RingBufferTest(unittest.TestCase):

    def setUp(self):
        self.a = RingBuffer(1, 5)
        self.a1 = RingBuffer(1,10)
        self.b = numpy.arange(3).reshape([1, 3])
        self.c = numpy.arange(7).reshape([1, 7])
        self.d = numpy.arange(10).reshape([5, 2])
        self.e = numpy.arange(10).reshape([1,10])

    def test_buffer_initialization(self):
        self.assertEqual(1, self.a.num_channels, self.a.all_data())
        self.assertEqual(5, self.a.length, self.a.all_data())
        self.assertEqual(0, self.a.num_unread_data_points(), self.a.all_data())
        self.assertTrue(numpy.array_equal(self.a.all_data(), numpy.zeros([1, 5])), self.a.all_data())
        self.assertEqual(self.a.write_position, 0, self.a.all_data())
        self.assertEqual(self.a.read_position, 0, self.a.all_data())

    def test_push_small(self):
        self.a.push(self.b)
        self.assertEqual(1, self.a.num_channels, self.a.all_data())
        self.assertEqual(5, self.a.length, self.a.all_data())
        self.assertEqual(3, self.a.num_unread_data_points(), self.a.all_data())
        self.assertEqual(self.a.write_position, 3, self.a.all_data())
        self.assertEqual(self.a.read_position, 0, self.a.all_data())
        self.assertTrue(numpy.array_equal(self.a.all_data(), numpy.array([[0., 1., 2., 0., 0.]])), self.a.all_data())

    def test_multi_push_into_small(self):
        self.a.push(self.b)
        self.a.push(self.b)
        self.assertEqual(1, self.a.num_channels, self.a.all_data())
        self.assertEqual(5, self.a.length, self.a.all_data())
        self.assertEqual(5, self.a.num_unread_data_points(), self.a.all_data())
        self.assertEqual(self.a.write_position, 1, self.a.all_data())
        self.assertEqual(self.a.read_position, 1, self.a.all_data())
        self.assertTrue(numpy.array_equal(self.a.all_data(), numpy.array([[2., 1., 2., 0., 1.]])), self.a.all_data())

    def test_multi_push_into_big(self):
        self.a1.push(self.b)
        self.a1.push(self.b)
        self.a1.push(self.b)
        self.assertEqual(1, self.a1.num_channels, self.a1.all_data())
        self.assertEqual(10, self.a1.length, self.a1.all_data())
        self.assertEqual(9, self.a1.num_unread_data_points(), self.a1.all_data())
        self.assertEqual(self.a1.write_position, 9, self.a1.all_data())
        self.assertEqual(self.a1.read_position, 0, self.a1.all_data())
        self.assertTrue(numpy.array_equal(self.a1.all_data(), numpy.array([
            [0., 1., 2., 0., 1., 2., 0., 1., 2., 0.]])), self.a1.all_data())

    def test_push_big(self):
        self.a.push(self.c)
        self.assertEqual(1, self.a.num_channels, self.a.all_data())
        self.assertEqual(5, self.a.length, self.a.all_data())
        self.assertEqual(5, self.a.num_unread_data_points(), self.a.all_data())
        self.assertEqual(self.a.write_position, 2, self.a.all_data())
        self.assertEqual(self.a.read_position, 2, self.a.all_data())
        self.assertTrue(numpy.array_equal(self.a.all_data(), numpy.array([[5., 6., 2., 3., 4.]])), self.a.all_data())

    def test_push_multi_channel_small(self):
        self.a.push(self.d)
        self.assertEqual(5, self.a.num_channels, self.a.all_data())
        self.assertEqual(5, self.a.length, self.a.all_data())
        self.assertEqual(2, self.a.num_unread_data_points(), self.a.all_data())
        self.assertEqual(self.a.write_position, 2, self.a.all_data())
        self.assertEqual(self.a.read_position, 0, self.a.all_data())
        self.assertTrue(numpy.array_equal(self.a.all_data(),
                                          numpy.array([[0., 1., 0., 0., 0.],
                                                       [2., 3., 0., 0., 0.],
                                                       [4., 5., 0., 0., 0.],
                                                       [6., 7., 0., 0., 0.],
                                                       [8., 9., 0., 0., 0.]])), self.a.all_data())

    def test_push_channel_number_change(self):
        self.a.push(self.b)
        self.a.push(self.d)
        self.assertEqual(5, self.a.num_channels, self.a.all_data())
        self.assertEqual(5, self.a.length, self.a.all_data())
        self.assertEqual(2, self.a.num_unread_data_points(), self.a.all_data())
        self.assertEqual(self.a.write_position, 2, self.a.all_data())
        self.assertEqual(self.a.read_position, 0, self.a.all_data())
        self.assertTrue(numpy.array_equal(self.a.all_data(),
                                          numpy.array([[0., 1., 0., 0., 0.],
                                                       [2., 3., 0., 0., 0.],
                                                       [4., 5., 0., 0., 0.],
                                                       [6., 7., 0., 0., 0.],
                                                       [8., 9., 0., 0., 0.]])), self.a.all_data())

    def test_multi_push_multi_channel(self):
        self.a.push(self.d)
        self.a.push(self.d)
        self.a.push(self.d)
        self.assertEqual(5, self.a.num_channels, self.a.all_data())
        self.assertEqual(5, self.a.length, self.a.all_data())
        self.assertEqual(5, self.a.num_unread_data_points(), self.a.all_data())
        self.assertEqual(self.a.write_position, 1, self.a.all_data())
        self.assertEqual(self.a.read_position, 1, self.a.all_data())
        self.assertTrue(numpy.array_equal(self.a.all_data(),
                                          numpy.array([[1., 1., 0., 1., 0.],
                                                       [3., 3., 2., 3., 2.],
                                                       [5., 5., 4., 5., 4.],
                                                       [7., 7., 6., 7., 6.],
                                                       [9., 9., 8., 9., 8.]])), self.a.all_data())

    def test_pop_single(self):
        self.a1.push(self.e)
        data = self.a1.pop(5)
        self.assertTrue(numpy.array_equal(data, numpy.array([[0., 1., 2., 3., 4.]])), self.a1.all_data())
        self.assertEqual(1, self.a1.num_channels, self.a1.all_data())
        self.assertEqual(10, self.a1.length, self.a1.all_data())
        self.assertEqual(5, self.a1.num_unread_data_points(), self.a1.all_data())
        self.assertEqual(self.a1.write_position, 0, self.a1.all_data())
        self.assertEqual(self.a1.read_position, 5, self.a1.all_data())
        self.assertTrue(numpy.array_equal(self.a1.all_data(), numpy.array([
            [0., 1., 2., 3., 4., 5., 6., 7., 8., 9.]])), self.a1.all_data())

    def test_pop_multi(self):
        self.a1.push(self.e)
        self.a1.pop(5)
        self.a1.pop(5)
        data = self.a1.pop(5)
        self.assertTrue(numpy.array_equal(data, numpy.array([[0., 1., 2., 3., 4.]])), self.a1.all_data())
        self.assertEqual(1, self.a1.num_channels, self.a1.all_data())
        self.assertEqual(10, self.a1.length, self.a1.all_data())
        self.assertEqual(0, self.a1.num_unread_data_points(), self.a1.all_data())
        self.assertEqual(self.a1.write_position, 0, self.a1.all_data())
        self.assertEqual(self.a1.read_position, 5, self.a1.all_data())
        self.assertTrue(numpy.array_equal(self.a1.all_data(), numpy.array([
            [0., 1., 2., 3., 4., 5., 6., 7., 8., 9.]])), self.a1.all_data())

if __name__ == "__main__":
    unittest.main()