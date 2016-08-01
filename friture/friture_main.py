import sys
import os
import os.path
import platform

from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QPixmap

from friture.logger import Logger  # Logging class
from friture.analyzer import Friture


def main():
    print("Platform is %s (%s)" %(platform.system(), sys.platform))

    if platform.system() == "Windows":
        print("Applying Windows-specific setup")
        # On Windows, redirect stderr to a file
        import imp
        import ctypes
        if (hasattr(sys, "frozen") or  # new py2exe
                hasattr(sys, "importers") or  # old py2exe
                imp.is_frozen("__main__")):  # tools/freeze
            sys.stderr = open(os.path.expanduser("~/friture.exe.log"), "w")
        # set the App ID for Windows 7 to properly display the icon in the
        # taskbar.
        myappid = 'Friture.Friture.Friture.current'  # arbitrary string
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except:
            print("Could not set the app model ID. If the plaftorm is older than Windows 7, this is normal.")

    app = QApplication(sys.argv)

    if platform.system() == "Darwin":
        if hasattr(sys, "frozen"): #py2app
            sys.stdout = open(os.path.expanduser("~/friture.out.txt"), "w")
            sys.stderr = open(os.path.expanduser("~/friture.err.txt"), "w")

        print("Applying Mac OS-specific setup")
        # help the py2app-packaged application find the Qt plugins (imageformats and platforms)
        pluginsPath = os.path.normpath(os.path.join(QApplication.applicationDirPath(), os.path.pardir, 'PlugIns'))
        print("Adding the following to the Library paths: " + pluginsPath)
        QApplication.addLibraryPath(pluginsPath)

    # Splash screen
    pixmap = QPixmap(":/images/splash.png")
    splash = QSplashScreen(pixmap)
    splash.show()
    splash.showMessage("Initializing the audio subsystem")
    app.processEvents()

    # Logger class
    logger = Logger(verbose=True)

    window = Friture(logger)
    window.show()
    splash.finish(window)

    profile = "no"  # "python" or "kcachegrind" or anything else to disable

    if len(sys.argv) > 1:
        if sys.argv[1] == "--python":
            profile = "python"
        elif sys.argv[1] == "--kcachegrind":
            profile = "kcachegrind"
        elif sys.argv[1] == "--no":
            profile = "no"
        else:
            print("command-line arguments (%s) not recognized" % sys.argv[1:])

    if profile == "python":
        import cProfile
        import pstats

        cProfile.runctx('app.exec_()', globals(), locals(), filename="friture.cprof")

        stats = pstats.Stats("friture.cprof")
        stats.strip_dirs().sort_stats('time').print_stats(20)
        stats.strip_dirs().sort_stats('cumulative').print_stats(20)

        sys.exit(0)
    elif profile == "kcachegrind":
        import cProfile
        import lsprofcalltree

        p = cProfile.Profile()
        p.run('app.exec_()')

        k = lsprofcalltree.KCacheGrind(p)
        with open('cachegrind.out.00000', 'wb') as data:
            k.output(data)

        sys.exit(0)
    else:
        sys.exit(app.exec_())