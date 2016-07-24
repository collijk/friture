from PyQt5.QtWidgets import QWidget
from friture.ui_playback_widget import PlaybackWidgetUI


class PlaybackWidget(QWidget, PlaybackWidgetUI):

    def __init__(self, parent = None):
        super(PlaybackWidget, self).__init__(parent)
        self.setupUi(self)


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    w = PlaybackWidget
    w.show()
    sys.exit(app.exec_())
