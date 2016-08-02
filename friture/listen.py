from PyQt5 import QtCore, QtWidgets
from friture.ui_listen_widget import ListenWidgetUI
from friture.logger import PrintLogger


class ListenWidget(QtWidgets.QWidget, ListenWidgetUI):
    """Widget providing controls for listening to microphone input and recording/playing audio snippets.

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
    idle_signal = QtCore.pyqtSignal(int)
    listening_signal = QtCore.pyqtSignal(int)
    recording_signal = QtCore.pyqtSignal(int)
    playing_signal = QtCore.pyqtSignal(int)

    # Data signals
    clear_data_signal = QtCore.pyqtSignal()

    # Device signals
    input_device_changed_signal = QtCore.pyqtSignal(int)
    input_channel_type_changed_signal = QtCore.pyqtSignal(int)
    output_device_changed_signal = QtCore.pyqtSignal(int)

    def __init__(self, parent=None, logger=PrintLogger()):
        super(ListenWidget, self).__init__(parent)
        self.setupUi(self)
        self._logger = logger
        self._data_available_for_playback = False
        self._state = ListenWidget.IDLE
        self._connect_ui()

    def add_input_devices(self, input_devices, current_device_index):
        """Adds audio input devices to this widgets input device combo box.

        Parameters
        ----------
        input_devices : list of str
            A readable list of the available input devices.
        current_device_index : int
            The currently selected input device.

        """
        self.comboBox_input_device.addItems(input_devices)
        self.comboBox_input_device.setCurrentIndex(current_device_index)
        self.comboBox_input_device.setEnabled(True)
        self.comboBox_input_device.currentIndexChanged.connect(self._input_device_changed)

    def add_output_devices(self, output_devices, current_device_index):
        """Adds audio output devices to this widgets output device combo box.

        Parameters
        ----------
        output_devices : list of str
            A readable list of the available input devices.
        current_device_index : int
            The currently selected input device.

        """
        self.comboBox_output_device.addItems(output_devices)
        self.comboBox_output_device.setCurrentIndex(current_device_index)
        self.comboBox_output_device.setEnabled(True)
        self.comboBox_input_device.currentIndexChanged.connect(self._output_device_changed)

    def disconnect_all_signals(self):
        self._disconnect_signal(self.idle_signal)
        self._disconnect_signal(self.listening_signal)
        self._disconnect_signal(self.recording_signal)
        self._disconnect_signal(self.playing_signal)
        self._disconnect_signal(self.clear_data_signal)
        self._disconnect_signal(self.input_device_changed_signal)
        self._disconnect_signal(self.output_device_changed_signal)
        self._disconnect_signal(self.input_channel_type_changed_signal)

    @staticmethod
    def _disconnect_signal(signal):
        while True:
            try:
                signal.disconnect()
            except TypeError:  # The signal is not connected to anything
                break

    def get_state(self):
        """Returns the current state of this widget."""
        return self._state

    def canvas_update(self):
        """Updates this widgets display"""
        self.time_plot.canvas_update()

    def save_state(self, settings):
        """Save the current widget configuration

        Parameters
        ----------
        settings : :class:`QSettings`
            The application settings object to be written to.

        """
        # TODO: Implement settings saving.
        pass

    def restore_state(self, settings):
        """Restore the current widget's configuration from settings

        Parameters
        ----------
        settings : :class:`QSettings`
            The application settings object from which this widgets settings may be loaded.

        """
        # TODO: Implement settings loading.
        pass

    def _connect_ui(self):
        self.button_listen.released.connect(self._listen_button_pressed)
        self.button_record_and_stop.released.connect(self._record_button_pressed)
        self.button_clear.released.connect(self._clear_button_pressed)
        self.button_playback_and_stop.released.connect(self._play_button_pressed)
        self.button_save.released.connect(self._save_button_pressed)

        # TODO: Connect radio buttons to signals

        self.idle_signal.connect(self._change_state_to_idle)
        self.listening_signal.connect(self._change_state_to_listening)
        self.recording_signal.connect(self._change_state_to_recording)
        self.playing_signal.connect(self._change_state_to_playing)
        self.clear_data_signal.connect(self._data_cleared)

    def _listen_button_pressed(self):
        if self._state == ListenWidget.IDLE:
            self.listening_signal.emit(self._state)
        elif self._state == ListenWidget.LISTENING:
            self.idle_signal.emit(self._state)
        elif self._state == ListenWidget.RECORDING:
            self.idle_signal.emit(self._state)
        # else self._state == ListenWidget.PLAYING: listen button should be inactive

    def _record_button_pressed(self):
        # if self._state == ListenWidget.IDLE: record button should be inactive
        if self._state == ListenWidget.LISTENING:
            self.recording_signal.emit(self._state)
        elif self._state == ListenWidget.RECORDING:
            self.listening_signal.emit(self._state)
        # else: self._state == ListenWidget.PLAYING: record button should be inactive

    def _clear_button_pressed(self):
        if self._data_available_for_playback:
            self.clear_data_signal.emit()
        # else: clear button should be inactive

    def _play_button_pressed(self):
        if self._data_available_for_playback:
            if self._state == ListenWidget.IDLE:
                self.playing_signal.emit(self._state)
            # elif self._state == ListeningWidget.LISTENING: play button should be inactive
            # elif self._state == ListeningWidget.RECORDING: play button should be inactive
            elif self._state == ListenWidget.PLAYING:
                self.idle_signal.emit(self._state)
        # else: play button should be inactive

    def _save_button_pressed(self):
        if self._data_available_for_playback:
            # TODO: Make saving data work
            pass

    def _input_device_changed(self, index):
        self.input_device_changed_signal.emit(index)

    def _output_device_changed(self, index):
        self.output_device_changed_signal.emit(index)

    def _change_state_to_idle(self, previous_state):

        self.button_listen.setText("Listen")
        self.button_listen.setEnabled(True)

        self.button_record_and_stop.setEnabled(False)

        self.comboBox_input_device.setEnabled(True)
        self.comboBox_output_device.setEnabled(True)
        self.radioButton_single_channel.setEnabled(True)
        self.radioButton_dual_channel.setEnabled(True)

        if self._data_available_for_playback:
            self.button_playback_and_stop.setEnabled(True)
            self.button_save.setEnabled(True)
            self.button_playback_and_stop.setText("Play")
            self.button_clear.setEnabled(True)

        if previous_state == ListenWidget.IDLE:
            pass  # Shouldn't be able to get here.
        elif previous_state == ListenWidget.LISTENING:
            pass  # Covered by defaults.
        elif previous_state == ListenWidget.RECORDING:
            self.button_record_and_stop.setText("Record")
        elif previous_state == ListenWidget.PLAYING:
            pass  # Covered by defaults.

        self._state = ListenWidget.IDLE

    def _change_state_to_listening(self, previous_state):

        self.comboBox_input_device.setEnabled(False)
        self.radioButton_single_channel.setEnabled(False)
        self.radioButton_dual_channel.setEnabled(False)

        self.button_playback_and_stop.setEnabled(False)
        self.button_record_and_stop.setEnabled(True)
        self.button_listen.setText("Stop Listening")

        if previous_state == ListenWidget.IDLE:
            pass  # Covered by default
        elif previous_state == ListenWidget.LISTENING:
            pass  # Shouldn't be able to get here.
        elif previous_state == ListenWidget.RECORDING:
            self.button_record_and_stop.setText("Record")
            self.button_save.setEnabled(True)
        elif previous_state == ListenWidget.PLAYING:
            pass  # Shouldn't be able to get here.

        self._state = ListenWidget.LISTENING

    def _change_state_to_recording(self, previous_state):
        self.button_record_and_stop.setText("Stop Recording")
        self.button_clear.setEnabled(True)
        self.button_save.setEnabled(False)
        self.button_playback_and_stop.setEnabled(False)

        if previous_state == ListenWidget.IDLE:
            pass  # Shouldn't be able to get here.
        elif previous_state == ListenWidget.LISTENING:
            pass  # Covered by defaults.
        elif previous_state == ListenWidget.RECORDING:
            pass  # Shouldn't be able to get here.
        elif previous_state == ListenWidget.PLAYING:
            pass  # Shouldn't be able to get here.

        self._data_available_for_playback = True
        self._state = ListenWidget.RECORDING

    def _change_state_to_playing(self, previous_state):
        self.button_listen.setEnabled(False)
        self.button_clear.setEnabled(False)
        self.comboBox_output_device.setEnabled(False)
        self.button_playback_and_stop.setText("Stop Playback")

        if previous_state == ListenWidget.IDLE:
            pass
        elif previous_state == ListenWidget.LISTENING:
            pass  # Shouldn't be able to get here.
        elif previous_state == ListenWidget.RECORDING:
            pass  # Shouldn't be able to get here.
        elif previous_state == ListenWidget.PLAYING:
            pass  # Shouldn't be able to get here.

        self._state = ListenWidget.PLAYING

    def _data_cleared(self):
        if self._state == ListenWidget.RECORDING:
            return

        self._data_available_for_playback = False
        self.button_clear.setEnabled(False)
