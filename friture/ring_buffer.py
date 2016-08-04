import numpy


class RingBuffer(object):
    """A statically sized circular buffer"""

    def __init__(self, num_channels, length):
        self.num_channels = num_channels
        self.length = length
        self.data = numpy.zeros([num_channels, length])
        self.write_position = 0
        self.read_position = 0
        self.is_full = False

    def push(self, new_data):

        if new_data.shape[0] != self.num_channels:
            self.reset(new_data.shape[0], self.length)

        new_data_read_position = 0
        end_write_position = self.write_position + new_data.shape[1]
        adjust_read_position = False

        if end_write_position < self.length - 1:
            if self.read_position > self.write_position:
                adjust_read_position = end_write_position > self.read_position
        else:
            self.is_full = True
            while end_write_position > (self.length - 1):

                elements_to_write = self.length - self.write_position
                segment_end = new_data_read_position + elements_to_write
                self.data[:, self.write_position:] = new_data[:, new_data_read_position:segment_end]
                self.write_position = 0
                new_data_read_position += elements_to_write
                end_write_position -= self.length
                adjust_read_position = adjust_read_position or end_write_position > self.read_position

        self.data[:, self.write_position:end_write_position] = new_data[:, new_data_read_position:]
        self.write_position = end_write_position

        if adjust_read_position:
            self.read_position = self.write_position

    def pop(self, data_length):

        data_out = numpy.zeros([self.num_channels, data_length])

        out_write_position = 0
        end_read_position = self.read_position + data_length

        while end_read_position > (self.length - 1):
            elements_to_write = self.length - self.write_position
            segment_end = out_write_position + elements_to_write
            data_out[:, out_write_position:segment_end] = self.data[:, self.read_position:]
            out_write_position += elements_to_write
            end_read_position -= self.length
            self.read_position = 0

        data_out[:, out_write_position:] = self.data[:, self.read_position:end_read_position]
        self.read_position = end_read_position

        return data_out

    def all_data(self):
        return self.data

    def num_unread_data_points(self):
        if self.write_position >= self.read_position:
            return self.write_position - self.read_position
        else:
            return self.length - (self.read_position - self.write_position)

    def unwound_data(self):
        """Returns a linear array of the data, unwound and starting with the oldest data."""

        if self.is_full:
            return numpy.append(self.data[:, self.write_position:], self.data[:, :self.write_position])
        else:  # We haven't filled a buffer yet so start at the beginning.
            return self.data

    def reset(self, new_num_channels, new_length):
        self.num_channels = new_num_channels
        self.length = new_length
        self.data = numpy.zeros([self.num_channels, self.length])
        self.write_position = 0
        self.read_position = 0
        self.is_full = False













