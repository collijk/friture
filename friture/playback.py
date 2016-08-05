from friture.audio_io_widget import AudioIOWidget
from friture.logger import PrintLogger
from friture.ui_playback_widget import PlaybackWidgetUI

# FIXME:
# The widget needs to be modified to receive feedback, ie a file is actually opened when the load button is
# pressed.  Currently we just assume so.


class PlaybackWidget(AudioIOWidget, PlaybackWidgetUI):
    """Widget providing controls for loading audio files and playing them.

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
        super(PlaybackWidget, self).__init__(parent)
        self.setupUi(self)
        self._logger = logger
        self._data_available_for_playback = False

        self._connect_ui()
        self._connect_internal_signals()

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
        self.comboBox_output_device.currentIndexChanged.connect(self._output_device_changed)

    def change_output_device(self, device_index):
        super().change_output_device(device_index)
        current_device_index = self.comboBox_output_device.currentIndex()
        if device_index == current_device_index:
            pass  # Everything is peachy, device was changed successfully.
        else:
            self.comboBox_output_device.setCurrentIndex(device_index)
            self._logger.push("Device change unsuccessful, reverting to previous output device.")

    def canvas_update(self):
        """Updates this widgets display"""
        super().canvas_update()

        self.time_plot.canvas_update()

    def disconnect_all_signals(self):
        """Disconnects all external slots from this widget's signals"""
        super().disconnect_all_signals()

        self._connect_internal_signals()

    def _connect_ui(self):
        self.button_load.released.connect(self._load_button_pressed)
        self.button_playback_and_stop.released.connect(self._play_button_pressed)
        self.button_clear.released.connect(self._clear_button_pressed)

    def _connect_internal_signals(self):
        self.idle_signal.connect(self._change_state_to_idle)
        self.playing_signal.connect(self._change_state_to_playing)
        self.clear_data_signal.connect(self._clear_data)
        self.load_data_signal.connect(self._load_data)

    def _load_button_pressed(self):
        self.load_data_signal.emit()

    def _play_button_pressed(self):
        if self._state == PlaybackWidget.IDLE:
            self.playing_signal.emit()
        elif self._state == PlaybackWidget.PLAYING:
            self.idle_signal.emit()

    def _clear_button_pressed(self):
        self.clear_data_signal.emit()

    def _output_device_changed(self, index):
        self.output_device_changed_signal.emit(index)

    def _change_state_to_idle(self):

        self.comboBox_output_device.setEnabled(True)
        self.button_playback_and_stop.setText("Play")
        if self._data_available_for_playback:
            self.button_clear.setEnabled(True)
        self.button_load.setEnabled(True)

        self._state = PlaybackWidget.IDLE

    def _change_state_to_playing(self):
        self.comboBox_output_device.setEnabled(False)
        self.button_clear.setEnabled(False)
        self.button_load.setEnabled(False)

        self.button_playback_and_stop.setText("Stop")

        self._state = PlaybackWidget.PLAYING

    def _clear_data(self):
        self._data_available_for_playback = False
        self.button_playback_and_stop.setEnabled(False)
        self.button_clear.setEnabled(False)

    def _load_data(self):
        self._data_available_for_playback = True
        self.button_playback_and_stop.setEnabled(True)
        self.button_clear.setEnabled(True)


