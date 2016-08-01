from PyQt5 import QtWidgets, QtCore
from friture.logger import PrintLogger
from friture.ui_playback_widget import PlaybackWidgetUI


class PlaybackWidget(QtWidgets.QWidget, PlaybackWidgetUI):
    """Widget providing controls for loading audio files and playing them.

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
    playing_signal :
        Emitted when this widget enters the playback from recording state.
    load_signal :
        Emitted when this widget requests a file to be loaded.
    clear_data_signal :
        Emitted when this widget requests recorded data to be deleted.
    output_device_changed_signal :
        Emitted when this widget request the output device to be changed.


    """

    # States for this widget.
    IDLE, PLAYING = range(2)

    # State change signals
    idle_signal = QtCore.pyqtSignal(int)
    playing_signal = QtCore.pyqtSignal(int)

    # Data signals
    load_signal = QtCore.pyqtSignal(int)
    clear_data_signal = QtCore.pyqtSignal()

    # Device signals
    output_device_change_signal = QtCore.pyqtSignal(int)

    def __init__(self, parent=None, logger=PrintLogger()):
        super(PlaybackWidget, self).__init__(parent)
        self.setupUi(self)
        self._logger = logger
        self._data_available_for_playback = False
        self._state = PlaybackWidget.IDLE

        self._connect_ui()

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
        self.comboBox_output_device.currentIndexChanged.connect(self._output_device_changed)
        
    def get_state(self):
        """Returns this widget's current state"""
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
        self.button_load.released.connect(self._load_button_pressed)
        self.button_playback_and_stop.released.connect(self._play_button_pressed)
        self.button_clear.released.connect(self._clear_button_pressed)

        self.idle_signal.connect(self._change_state_to_idle)
        self.playing_signal.connect(self._change_state_to_playing)

    def _load_button_pressed(self):
        # TODO: Implement file loading logic
        self._data_available_for_playback = True
        if self._data_available_for_playback:
            self.button_playback_and_stop.setEnabled(True)
            self.button_clear.setEnabled(True)

    def _play_button_pressed(self):
        if self._state == PlaybackWidget.IDLE:
            self.playing_signal.emit(self._state)
        elif self._state == PlaybackWidget.PLAYING:
            self.playing_signal.emit(self._state)

    def _clear_button_pressed(self):
        self.clear_data_signal.emit()
        self._data_available_for_playback = False
        self.button_playback_and_stop.setEnabled(False)
        self.button_clear.setEnabled(False)

    def _output_device_changed(self, index):
        self.output_device_changed_signal.emit(index)

    def _change_state_to_idle(self, previous_state):
        self.comboBox_output_device.setEnabled(True)
        self.button_playback_and_stop.setText("Play")
        self.button_clear.setEnabled(True)
        self.button_load.setEnabled(True)
        self._state = PlaybackWidget.IDLE

    def _change_state_to_playing(self, previous_state):
        self.comboBox_output_device.setEnabled(False)
        self.button_playback_and_stop.setText("Stop")
        self.button_clear.setEnabled(False)
        self.button_load.setEnabled(False)
        self._state = PlaybackWidget.PLAYING

