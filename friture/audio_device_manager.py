from PyQt5 import QtCore


class AudioDeviceManager(QtCore.QObject):
    """Wrapper class to manage audio devices.

    Parameters
    ----------
    pyaudio : :class:`PyAudio`
        The client application's instance of PyAudio
    logger : :class:`Logger`
        The client application _logger.

    Attributes
    ----------
    input_devices : list of :class:`AudioDevice`
        The devices available for audio input streams.
    output_devices : list of :class:`AudioDevice`
        The devices available for audio output streams.
    current_input_device : :class:`AudioDevice`
        The input device currently being used.
    current_output_device : :class:`AudioDevice`
        The output device currently being used.

    """
    def __init__(self, pyaudio, logger):
        super(AudioDeviceManager, self).__init__()

        self._pyaudio = pyaudio
        self._logger = logger
        logger.push("Initializing Device Manager")
        self.input_devices, self.output_devices = self._get_audio_io_devices()
        self.current_input_device = None
        self.current_output_device = None

    def get_current_input_device(self):
        return self.current_input_device

    def get_input_device(self, index):
        return self.input_devices[index]

    def get_current_input_device_index(self):
        return self.input_devices.index(self.current_input_device)

    def get_input_devices(self):
        return self.input_devices

    def set_current_input_device(self, device):
        self.current_input_device = device

    def get_current_output_device(self):
        return self.current_output_device

    def get_output_device(self, index):
        return self.output_devices[index]

    def get_current_output_device_index(self):
        return self.output_devices.index(self.current_output_device)

    def get_output_devices(self):
        return self.output_devices

    def set_current_output_device(self, index):
        self.current_output_device = self.output_devices[index]

    def input_is_dual_channel(self):
        return self.current_input_device.input_is_dual_channel

    def set_single_channel_input(self):
        self.current_input_device.input_is_dual_channel = False

    def set_dual_channel_input(self):
        self.current_input_device.input_is_dual_channel = True

    def get_input_channels(self):
        return self.current_input_device.input_channels

    def get_first_input_channel(self):
        return self.current_input_device.first_channel

    def get_second_input_channel(self):
        return self.current_input_device.second_channel

    def set_first_input_channel(self, index):
        self.current_input_device.first_channel = index

    def set_second_input_channel(self, index):
        self.current_input_device.second_channel = index

    def get_readable_input_devices(self):
        return [str(device) for device in self.input_devices]

    def get_readable_output_devices(self):
        return [str(device) for device in self.output_devices]

    def _get_audio_io_devices(self):
        """Retrieves a list of input and output devices available on the system.

        Returns
        -------
        input_devices : list of :class:`AudioDevice`
            The available input devices on the system.
        output_devices : list of :class:`AudioDevice`
            The available output devices on the system.

        """
        # Get raw information about the devices available on the system.
        device_range = list(range(0, self._pyaudio.get_device_count()))
        infos = [self._pyaudio.get_device_info_by_index(device) for device in device_range]
        apis = [self._pyaudio.get_host_api_info_by_index(info['hostApi'])['name'] for info in infos]

        # Construct an audio device wrapper for each device.
        all_devices = [AudioDevice(device, infos[device], apis[device]) for device in device_range]

        # Separate input and output devices into different lists.
        input_devices = self._get_devices(all_devices, AudioDevice.INPUT)
        output_devices = self._get_devices(all_devices, AudioDevice.OUTPUT)

        return input_devices, output_devices

    def _get_devices(self, all_devices, device_type):
        """Retrieves a list of devices of the appropriate device i/o type.

        Parameters
        ----------
        all_devices : list of :class:`AudioDevice`
            All audio devices available on the current system.
        device_type : {`AudioDevice.INPUT`, `AudioDevice.OUTPUT`}
            The i/o type of the requested devices.

        Returns
        -------
        devices : list of :class:`AudioDevice`
            A pared down list of devices of the requested i/o type with the default device at the front.
        """

        devices = []
        # Get the system default device for this i/o type
        default_device = self._get_default_device(device_type)

        for device in all_devices:
            if device.type == device_type or device.type == AudioDevice.IO:
                devices += [device]
                # Now see if this device is also the system default for the i/o type
                if default_device is not None and all_devices.index(device) == default_device:
                    device.is_default = True  # Flag the device if so
                    devices.insert(0, devices.pop())  # And move it to the front of the list
        return devices

    def _get_default_device(self, device_type):
        """Finds the index of the system default device for an i/o type.

        Parameters
        ----------
        device_type : {`AudioDevice.INPUT`, `AudioDevice.OUTPUT`}
            The i/o type of the requested devices.

        Returns
        -------
        int or None
            int if the system has a default device for the requested i/o type, None otherwise.

        """
        try:
            if device_type == AudioDevice.INPUT:
                return self._pyaudio.get_default_input_device_info()['index']
            else:  # device_type == AudioDevice.OUTPUT
                return self._pyaudio.get_default_output_device_info()['index']
        except IOError:
            return None

    def __repr__(self):
        return ("%s" % self.__class__).join(
            ["%r" % device for device in self.input_devices]).join(
            ["%r" % device for device in self.output_devices])


class AudioDevice(object):
    """Represents a system audio device.

    Parameters
    ----------
    index : int
        The index by which PyAudio finds the device.
    info : dict
        The audio device info. The keys of the dictionary mirror the data
        fields of PortAudio’s `PaDeviceInfo` structure.
    name : str
        The system name for the audio device.

    Attributes
    ----------
    index : int
        The index by which PyAudio finds the device.
    info : dict
        The audio device info. The keys of the dictionary mirror the data
        fields of PortAudio’s `PaDeviceInfo` structure.
    name : str
        The system name for the audio device.
    type : {`AudioDevice.INPUT`, `AudioDevice.OUTPUT`, `AudioDevice.IO`}
        The type of i/o the device is capable of.
    is_default : bool
        Whether this device is the system default for it's i/o type.
    num_input_channels, num_output_channels: int
        Number of channels available on this device for the i/o type.

    """

    (INPUT, OUTPUT, IO) = range(0, 3)
    """Possible types for the device."""

    def __init__(self, index, info, api):
        self.index = index
        self.info = info
        self.api = api
        self.type = None
        self.is_default = False

        self.input_channels = None
        self.output_channels = None

        self.input_is_dual_channel = False
        self.first_channel = None
        self.second_channel = None

        self.num_input_channels = self.info['maxInputChannels']
        self.num_output_channels = self.info['maxOutputChannels']

        self._set_io_type()

    def _get_input_channels(self):
        if self.num_input_channels == 2:
            self.input_channels = ['L', 'R']
            self.first_channel, self.second_channel = 0, 1
        else:
            self.input_channels = ["Channel %d" % channel for channel in range(0, self.num_input_channels)]
            self.first_channel, self.second_channel = 0, 0

    def _get_output_channels(self):
        if self.num_output_channels == 2:
            return ['L', 'R']
        else:
            return ["Channel %d" % channel for channel in range(0, self.num_output_channels)]

    def _set_io_type(self):
        """Sets the I/O type for the device based on the number of channels available for the i/o type."""
        if self.num_input_channels and self.num_output_channels:
            self.type = AudioDevice.IO
            self._get_input_channels()
            self._get_output_channels()
        elif self.num_input_channels:
            self.type = AudioDevice.INPUT
            self._get_input_channels()
        elif self.num_output_channels:
            self.type = AudioDevice.OUTPUT
            self._get_output_channels()
        else:
            self.type = None

    def __repr__(self):
        extra_info = ' (system default)' if self.is_default else ''
        return "%s (%d in channels, %d out channels) (%s) %s" % (
            self.info["name"], self.num_input_channels, self.num_output_channels, self.api, extra_info)

    def __str__(self):
        return repr(self)
