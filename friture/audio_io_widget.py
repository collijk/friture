from PyQt5 import QtCore, QtWidgets


class AudioIOWidget(QtWidgets. QWidget):
    """Widget providing essential signals and slots for audio_io

        Parameters
        ----------
        parent : :class:`QWidget` or :class:`QMainWindow`, optional
            The parent of this widget.
        logger : :class:`Logger`, optional
            The application _logger. Defaults to a simple print _logger.

        Signals
        -------
        idle_signal :
            Emitted when this widget enters the idle state
        listening_signal :
            Emitted when this widget enters the listening to microphone input state.
        recording_signal :
            Emitted when this widget enters the recording from microphone state.
        playing_signal :
            Emitted when this widget enters the playback from recording state.
        clear_data_signal :
            Emitted when this widget requests recorded data to be deleted.
        input_device_changed_signal :
            Emitted when this widget requests the input device to be changed.
        input_channel_type_changed_signal :
            Emitted when this widget requests the input channel type (single or dual) to be changed.
        output_device_changed_signal :
            Emitted when this widget request the output device to be changed.

        """

    # States for this widget.
    IDLE, LISTENING, RECORDING, PLAYING = range(4)

    # State signals
    idle_signal = QtCore.pyqtSignal()
    listening_signal = QtCore.pyqtSignal()
    recording_signal = QtCore.pyqtSignal()
    playing_signal = QtCore.pyqtSignal()

    # Data signals
    save_data_signal = QtCore.pyqtSignal()
    load_data_signal = QtCore.pyqtSignal()
    clear_data_signal = QtCore.pyqtSignal()

    # Device signals
    input_device_changed_signal = QtCore.pyqtSignal(int)
    input_channel_number_changed_signal = QtCore.pyqtSignal(int)
    output_device_changed_signal = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._state = AudioIOWidget.IDLE

    def get_state(self):
        """Returns the current state of this widget"""
        return self._state

    def add_input_devices(self, input_devices, current_device_index):
        pass

    def add_output_devices(self, output_device, current_device_index):
        pass

    def disconnect_all_signals(self):
        """Disconnects all external slots from this widget's signals"""
        self.disconnect_signal(self.idle_signal)
        self.disconnect_signal(self.listening_signal)
        self.disconnect_signal(self.recording_signal)
        self.disconnect_signal(self.playing_signal)

        self.disconnect_signal(self.save_data_signal)
        self.disconnect_signal(self.load_data_signal)
        self.disconnect_signal(self.clear_data_signal)

        self.disconnect_signal(self.input_device_changed_signal)
        self.disconnect_signal(self.output_device_changed_signal)
        self.disconnect_signal(self.input_channel_number_changed_signal)

    def canvas_update(self):
        pass

    def save_state(self, settings):
        pass

    def restore_state(self, settings):
        pass

    @staticmethod
    def disconnect_signal(signal):
        try:
            signal.disconnect()
        except TypeError:  # The signal is not connected to anything
            pass
