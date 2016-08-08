import numpy


class LinearBuffer(object):
    """A dynamically sized linear buffer."""

    def __init__(self, num_channels, length):
        self.num_channels = num_channels
        self.length = length
        self.data = numpy.zeros([num_channels, length], dtype=numpy.float32)
        self.write_position = 0
        self.read_position = 0
        self.unread_data_points = 0

    def push(self, new_data):

        self.unread_data_points += new_data.shape[1]
        self._grow_if_needed(new_data.shape[1])

        if new_data.shape[0] != self.num_channels:
            self.reset(new_data.shape[0], self.length)

        self.data[:, self.write_position:self.write_position + new_data.shape[1]] = new_data[:, :]
        self.write_position += new_data.shape[1]

    def pop(self, data_length):

        # If they've requested to much data, give them everything we have and zero fill the rest.
        if data_length > self.unread_data_points:
            zero_fill_length = data_length - self.unread_data_points
            data_out = numpy.append(self.data[:, self.read_position:self.write_position],
                                    numpy.zeros([self.num_channels, zero_fill_length])).reshape([self.num_channels,
                                                                                                 data_length])
            self.read_position = self.write_position
        else:
            data_out = self.data[:, self.read_position:self.read_position + data_length]
            self.read_position += data_length

        self.unread_data_points = max(0, self.unread_data_points - data_length)
        return data_out, self.unread_data_points

    def all_data(self):
        return self.data[:, :self.write_position]

    def reset_read_position(self, position):
        self.read_position = position
        self.unread_data_points = self.write_position - self.read_position

    def num_unread_data_points(self):
        return self.unread_data_points

    def reset(self, new_num_channels, new_length):
        self.num_channels = new_num_channels
        self.length = new_length
        self.data = numpy.zeros([self.num_channels, self.length])
        self.write_position = 0
        self.read_position = 0
        self.unread_data_points = 0

    def _grow_if_needed(self, new_data_length):
        while self.length <= (self.write_position + new_data_length):
            self.data = numpy.append(self.data, numpy.zeros([self.num_channels, self.length])).reshape(
                [self.num_channels, 2*self.length])

            self.length *= 2











