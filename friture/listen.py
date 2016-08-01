from PyQt5 import QtCore, QtWidgets
from friture.ui_listen_widget import ListenWidgetUI
from friture.logger import PrintLogger


class ListenWidget(QtWidgets.QWidget, ListenWidgetUI):

    IDLE, LISTENING, RECORDING, PLAYING = range(4)

    idle_signal = QtCore.pyqtSignal(int)
    listening_signal = QtCore.pyqtSignal(int)
    recording_signal = QtCore.pyqtSignal(int)
    playing_signal = QtCore.pyqtSignal(int)
    clear_data_signal = QtCore.pyqtSignal()

    input_device_changed_signal = QtCore.pyqtSignal(int)
    input_channel_type_changed_signal = QtCore.pyqtSignal(int)
    output_device_changed_signal = QtCore.pyqtSignal(int)


    def __init__(self, parent=None, logger=PrintLogger()):
        super(ListenWidget, self).__init__(parent)
        self.setupUi(self)
        self.logger = logger
        self.state = ListenWidget.IDLE
        self.data_available_for_playback = False

        self._connect_ui()




    def _connect_ui(self):
        self.button_listen.released.connect(self.listen_button_pressed)
        self.button_record_and_stop.released.connect(self.record_button_pressed)
        self.button_clear.released.connect(self.clear_button_pressed)
        self.button_playback_and_stop.released.connect(self.play_button_pressed)
        self.button_save.released.connect(self.save_button_pressed)

        # TODO: Connect radio buttons to signals

        self.idle_signal.connect(self.change_state_to_idle)
        self.listening_signal.connect(self.change_state_to_listening)
        self.recording_signal.connect(self.change_state_to_recording)
        self.playing_signal.connect(self.change_state_to_playing)
        self.clear_data_signal.connect(self.data_cleared)

    def add_input_devices(self, input_devices, current_device_index):
        self.comboBox_input_device.addItems(input_devices)
        self.comboBox_input_device.setCurrentIndex(current_device_index)
        self.comboBox_input_device.setEnabled(True)
        self.comboBox_input_device.currentIndexChanged.connect(self.input_device_changed)

    def add_output_devices(self, output_devices, current_device_index):
        self.comboBox_output_device.addItems(output_devices)
        self.comboBox_output_device.setCurrentIndex(current_device_index)
        self.comboBox_output_device.setEnabled(True)
        self.comboBox_input_device.currentIndexChanged.connect(self.output_device_changed)

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

    def listen_button_pressed(self):
        if self.state == ListenWidget.IDLE:
            self.listening_signal.emit(self.state)
        elif self.state == ListenWidget.LISTENING:
            self.idle_signal.emit(self.state)
        elif self.state == ListenWidget.RECORDING:
            self.idle_signal.emit(self.state)
        # else self.state == ListenWidget.PLAYING: listen button should be inactive

    def record_button_pressed(self):
        # if self.state == ListenWidget.IDLE: record button should be inactive
        if self.state == ListenWidget.LISTENING:
            self.recording_signal.emit(self.state)
        elif self.state == ListenWidget.RECORDING:
            self.listening_signal.emit(self.state)
        # else: self.state == ListenWidget.PLAYING: record button should be inactive

    def clear_button_pressed(self):
        if self.data_available_for_playback:
            self.clear_data_signal.emit()
        # else: clear button should be inactive

    def play_button_pressed(self):
        if self.data_available_for_playback:
            if self.state == ListenWidget.IDLE:
                self.playing_signal.emit(self.state)
            # elif self.state == ListeningWidget.LISTENING: play button should be inactive
            # elif self.state == ListeningWidget.RECORDING: play button should be inactive
            elif self.state == ListenWidget.PLAYING:
                self.idle_signal.emit(self.state)
        # else: play button should be inactive

    def save_button_pressed(self):
        if self.data_available_for_playback:
            # TODO: Make saving data work
            pass

    def input_device_changed(self, index):
        self.input_device_changed_signal.emit(index)

    def output_device_changed(self, index):
        self.output_device_changed_signal.emit(index)

    def change_state_to_idle(self, previous_state):

        self.button_listen.setText("Listen")
        self.button_listen.setEnabled(True)

        self.button_record_and_stop.setEnabled(False)

        self.comboBox_input_device.setEnabled(True)
        self.comboBox_output_device.setEnabled(True)
        self.radioButton_single_channel.setEnabled(True)
        self.radioButton_dual_channel.setEnabled(True)

        if self.data_available_for_playback:
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

        self.state = ListenWidget.IDLE

    def change_state_to_listening(self, previous_state):

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

        self.state = ListenWidget.LISTENING

    def change_state_to_recording(self, previous_state):
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

        self.data_available_for_playback = True
        self.state = ListenWidget.RECORDING

    def change_state_to_playing(self, previous_state):
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

        self.state = ListenWidget.PLAYING

    def data_cleared(self):
        if self.state == ListenWidget.RECORDING:
            pass

        self.data_available_for_playback = False
        self.button_clear.setEnabled(False)

