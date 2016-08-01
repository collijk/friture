from PyQt5 import QtWidgets, QtCore
from friture.logger import PrintLogger
from friture.ui_playback_widget import PlaybackWidgetUI


class PlaybackWidget(QtWidgets.QWidget, PlaybackWidgetUI):

    IDLE, PLAYING = range(2)

    idle_signal = QtCore.pyqtSignal(int)
    play_signal = QtCore.pyqtSignal(int)
    load_signal = QtCore.pyqtSignal(int)
    clear_signal = QtCore.pyqtSignal()
    output_device_change_signal = QtCore.pyqtSignal(int)

    def __init__(self, parent=None, logger=PrintLogger()):
        super(PlaybackWidget, self).__init__(parent)
        self.setupUi(self)
        self.logger = logger
        self.data_available_for_playback = False
        self.state = PlaybackWidget.IDLE

        self._connect_ui()

    def _connect_ui(self):
        self.button_load.released.connect(self.load_button_pressed)
        self.button_playback_and_stop.released.connect(self.play_button_pressed)
        self.button_clear.released.connect(self.clear_button_pressed)

        self.idle_signal.connect(self.change_state_to_idle)
        self.play_signal.connect(self.change_state_to_playing)

    def add_output_devices(self, output_devices, current_device_index):
        self.comboBox_output_device.addItems(output_devices)
        self.comboBox_output_device.setCurrentIndex(current_device_index)
        self.comboBox_output_device.currentIndexChanged.connect(self.output_device_changed)

    def set_buffer(self, audio_buffer):
        pass

    def handle_new_data(self, floatdata):
        pass

    def canvasUpdate(self):
        pass

    def pause(self):
        pass

    def restart(self):
        pass

    def saveState(self, settings):
        pass

    def restoreState(self, settings):
        pass

    def load_button_pressed(self):
        # TODO: Implement file loading logic
        self.data_available_for_playback = True
        if self.data_available_for_playback:
            self.button_playback_and_stop.setEnabled(True)
            self.button_clear.setEnabled(True)

    def play_button_pressed(self):
        if self.state == PlaybackWidget.IDLE:
            self.play_signal.emit(self.state)
        elif self.state == PlaybackWidget.PLAYING:
            self.play_signal.emit(self.state)

    def clear_button_pressed(self):
        self.clear_signal.emit()
        self.data_available_for_playback = False
        self.button_playback_and_stop.setEnabled(False)
        self.button_clear.setEnabled(False)

    def output_device_changed(self, index):
        self.output_device_changed_signal.emit(index)

    def change_state_to_idle(self, previous_state):
        self.comboBox_output_device.setEnabled(True)
        self.button_playback_and_stop.setText("Play")
        self.button_clear.setEnabled(True)
        self.button_load.setEnabled(True)
        self.state = PlaybackWidget.IDLE

    def change_state_to_playing(self, previous_state):
        self.comboBox_output_device.setEnabled(False)
        self.button_playback_and_stop.setText("Stop")
        self.button_clear.setEnabled(False)
        self.button_load.setEnabled(False)
        self.state = PlaybackWidget.PLAYING

