from PyQt5.QtWidgets import QWidget
from friture.ui_listen_widget import ListenWidgetUI
from friture.logger import PrintLogger


class ListenWidget(QWidget, ListenWidgetUI):

    def __init__(self, parent=None, logger=PrintLogger()):
        super(ListenWidget, self).__init__(parent)
        self.setupUi(self)
        self.logger = logger

        self.listening = False
        self.recording = False
        self.playing = False

        self.button_listen.released.connect(self.listen_button_pressed)

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
        if self.button_listen.text() == "Listen":
            self.button_listen.setText("Stop Listening")
            self.button_record_and_stop.setEnabled(True)
        else:
            self.button_listen.setText("Listen")
            self.button_record_and_stop.setDisabled(True)


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    from friture.audiobackend import AudioBackend
    from friture.logger import  Logger
    from friture.audiobuffer import AudioBuffer
    import sys

    app = QApplication(sys.argv)
    log = Logger()
    backend = AudioBackend(log)
    buffer = AudioBuffer(log)
    w = ListenWidget(logger=log)
    w.show()
    sys.exit(app.exec_())