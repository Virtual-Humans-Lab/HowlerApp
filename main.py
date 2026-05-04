from sys import exit, argv
from PySide6.QtWidgets import QApplication
import mainWindow
import os, importlib, faulthandler, argparse

try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'com.vhlab.appbugios.dist.1'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A simple program.")
    parser.add_argument("-D", "--debug", action='store_true', help="Enable debug messages")

    args = parser.parse_args()
    
    app = QApplication(argv)

    mWindow = mainWindow.MainWindow(debug=args.debug)
    mWindow.show()
    
    if '_PYI_SPLASH_IPC' in os.environ and importlib.util.find_spec("pyi_splash"):
        import pyi_splash
        pyi_splash.close()
        
    exit(app.exec())