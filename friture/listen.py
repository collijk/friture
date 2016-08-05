from friture.audio_io_widget import AudioIOWidget
from friture.ui_listen_widget import ListenWidgetUI
from friture.logger import PrintLogger


class ListenWidget(AudioIOWidget, ListenWidgetUI):
    """Widget providing controls for listening to microphone input and recording/playing audio snippets.

    Parameters
    ----------
    parent : :class:`QWidget` or :class:`QMainWindow`, optional
        The parent of this widget.
    logger : :class:`Logger`, optional
        The application _logger. Defaults to a simple print _logger.

    See Also
    --------
    For available signals see :class:'~audio_io_widget.AudioIOWidget`

    """

    def __init__(self, parent=None, logger=PrintLogger()):
        super().__init__(parent)
        self.setupUi(self)
        self._logger = logger
        self._data_available_for_playback = False
        self._connect_ui()
        self._connect_internal_signals()

    def add_input_devices(self, input_devices, current_device_index):
        """Adds audio input devices to this widgets input device combo box.

        Parameters
        ----------
        input_devices : list of str
            A readable list of the available input devices.
        current_device_index : int
            The currently selected input device.

        """
        super().add_input_devices(input_devices, current_device_index)

        self.comboBox_input_device.addItems(input_devices)
        self.comboBox_input_device.setCurrentIndex(current_device_index)
        self.comboBox_input_device.setEnabled(True)
        self.comboBox_input_device.currentIndexChanged.connect(self._input_device_changed)

    def change_input_device(self, device_index):
        super().change_input_device(device_index)
        current_device_index = self.comboBox_input_device.currentIndex()
        if device_index == current_device_index:
            pass  # Everything is peachy, device was changed successfully.
        else:
            self.comboBox_input_device.setCurrentIndex(device_index)
            self._logger.push("Device change unsuccessful, reverting to previous input device.")

    def add_output_devices(self, output_devices, current_device_index):
        """Adds audio output devices to this widgets output device combo box.

        Parameters
        ----------
        output_devices : list of str
            A readable list of the available input devices.
        current_device_index : int
            The currently selected input device.

        """
        super().add_output_devices(output_devices, current_device_index)

        self.comboBox_output_device.addItems(output_devices)
        self.comboBox_output_device.setCurrentIndex(current_device_index)
        self.comboBox_output_device.setEnabled(True)
        self.comboBox_output_device.currentIndexChanged.connect(self._output_device_changed)

    def change_output_device(self, device_index):
        super().change_output_device(device_index)
        current_device_index = self.comboBox_output_device.currentIndex()
        if device_index == current_device_index:
            pass  # Everything is peachy, device was changed successfully.
        else:
            self.comboBox_output_device.setCurrentIndex(device_index)
            self._logger.push("Device change unsuccessful, reverting to previous output device.")


    def disconnect_all_signals(self):
        """Disconnects all external slots from this widget's signals"""
        super().disconnect_all_signals()

        self._connect_internal_signals()

    def canvas_update(self):
        """Updates this widgets display"""
        super().canvas_update()

        self.time_plot.canvas_update()

    def _connect_ui(self):
        self.button_listen.released.connect(self._listen_button_pressed)
        self.button_record_and_stop.released.connect(self._record_button_pressed)
        self.button_clear.released.connect(self._clear_button_pressed)
        self.button_playback_and_stop.released.connect(self._play_button_pressed)
        self.button_save.released.connect(self._save_button_pressed)
        # TODO: Connect radio buttons to signals

    def _connect_internal_signals(self):
        self.idle_signal.connect(self._change_state_to_idle)
        self.listening_signal.connect(self._change_state_to_listening)
        self.recording_signal.connect(self._change_state_to_recording)
        self.playing_signal.connect(self._change_state_to_playing)
        self.clear_data_signal.connect(self._clear_data)
        
    def _listen_button_pressed(self):
        if self._state == AudioIOWidget.IDLE:
            self.listening_signal.emit()
        elif self._state == AudioIOWidget.LISTENING:
            self.idle_signal.emit()
        elif self._state == AudioIOWidget.RECORDING:
            self.idle_signal.emit()
        # else self._state == AudioIOWidget.PLAYING: listen button should be inactive

    def _record_button_pressed(self):
        # if self._state == AudioIOWidget.IDLE: record button should be inactive
        if self._state == AudioIOWidget.LISTENING:
            self.recording_signal.emit()
        elif self._state == AudioIOWidget.RECORDING:
            self.listening_signal.emit()
        # else: self._state == AudioIOWidget.PLAYING: record button should be inactive

    def _clear_button_pressed(self):
        if self._data_available_for_playback:
            self.clear_data_signal.emit()
        # else: clear button should be inactive

    def _play_button_pressed(self):
        if self._data_available_for_playback:
            if self._state == AudioIOWidget.IDLE:
                self.playing_signal.emit()
            # elif self._state == ListeningWidget.LISTENING: play button should be inactive
            # elif self._state == ListeningWidget.RECORDING: play button should be inactive
            elif self._state == AudioIOWidget.PLAYING:
                self.idle_signal.emit()
        # else: play button should be inactive

    def _save_button_pressed(self):
        self.save_data_signal.emit()

    def _input_device_changed(self, index):
        self.input_device_change_request_signal.emit(index)

    def _output_device_changed(self, index):
        self.output_device_change_request_signal.emit(index)

    def _change_state_to_idle(self):

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

        if self._state == AudioIOWidget.IDLE:
            pass  # Shouldn't be able to get here.
        elif self._state == AudioIOWidget.LISTENING:
            pass  # Covered by defaults.
        elif self._state == AudioIOWidget.RECORDING:
            self.button_record_and_stop.setText("Record")
        elif self._state == AudioIOWidget.PLAYING:
            pass  # Covered by defaults.

        self._state = AudioIOWidget.IDLE

    def _change_state_to_listening(self):

        self.comboBox_input_device.setEnabled(False)
        self.radioButton_single_channel.setEnabled(False)
        self.radioButton_dual_channel.setEnabled(False)

        self.button_playback_and_stop.setEnabled(False)
        self.button_record_and_stop.setEnabled(True)
        self.button_listen.setText("Stop Listening")

        if self._state == AudioIOWidget.IDLE:
            pass  # Covered by default
        elif self._state == AudioIOWidget.LISTENING:
            pass  # Shouldn't be able to get here.
        elif self._state == AudioIOWidget.RECORDING:
            self.button_record_and_stop.setText("Record")
            self.button_save.setEnabled(True)
        elif self._state == AudioIOWidget.PLAYING:
            pass  # Shouldn't be able to get here.

        self._state = AudioIOWidget.LISTENING

    def _change_state_to_recording(self):
        self.button_record_and_stop.setText("Stop Recording")
        self.button_clear.setEnabled(True)
        self.button_save.setEnabled(False)
        self.button_playback_and_stop.setEnabled(False)

        if self._state == AudioIOWidget.IDLE:
            pass  # Shouldn't be able to get here.
        elif self._state == AudioIOWidget.LISTENING:
            pass  # Covered by defaults.
        elif self._state == AudioIOWidget.RECORDING:
            pass  # Shouldn't be able to get here.
        elif self._state == AudioIOWidget.PLAYING:
            pass  # Shouldn't be able to get here.

        self._data_available_for_playback = True
        self._state = AudioIOWidget.RECORDING

    def _change_state_to_playing(self):
        self.button_listen.setEnabled(False)
        self.button_clear.setEnabled(False)
        self.comboBox_output_device.setEnabled(False)
        self.button_playback_and_stop.setText("Stop Playback")

        if self._state == AudioIOWidget.IDLE:
            pass
        elif self._state == AudioIOWidget.LISTENING:
            pass  # Shouldn't be able to get here.
        elif self._state == AudioIOWidget.RECORDING:
            pass  # Shouldn't be able to get here.
        elif self._state == AudioIOWidget.PLAYING:
            pass  # Shouldn't be able to get here.

        self._state = AudioIOWidget.PLAYING

    def _clear_data(self):
        if self._state == AudioIOWidget.RECORDING:
            return

        self._data_available_for_playback = False
        self.button_clear.setEnabled(False)
        self.button_playback_and_stop.setEnabled(False)
        self.button_save.setEnabled(False)
