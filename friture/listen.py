from PyQt5.QtWidgets import QWidget
from friture.ui_listen_widget import ListenWidgetUI


class ListenWidget(QWidget, ListenWidgetUI):

    def __init__(self, audio_backend, logger, parent=None):
        super(ListenWidget, self).__init__(parent)
        self.setupUi(self)
        self.audio_backend = audio_backend
        self.logger = logger



if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    w = ListenWidget()
    w.show()
    sys.exit(app.exec_())