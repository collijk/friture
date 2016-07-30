from PyQt5.QtWidgets import QWidget
from friture.audiobackend import AudioBackend
from friture.audiobuffer import AudioBuffer
from friture.logger import Logger, PrintLogger
from friture.ui_playback_widget import PlaybackWidgetUI


class PlaybackWidget(QWidget, PlaybackWidgetUI):

    def __init__(self, parent=None, logger=PrintLogger()):
        super(PlaybackWidget, self).__init__(parent)
        self.setupUi(self)
        self.logger = logger

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


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    log = Logger()
    backend = AudioBackend(log)
    buffer = AudioBuffer(log)
    w = PlaybackWidget()
    w.show()
    sys.exit(app.exec_())
