import sys
import ctypes

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from gui.main_window import MainWindow
from utils.resource import resource_path

myappid = "monsterchip.kitfwflasher.1.0"

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
    myappid
)

app = QApplication(sys.argv)

app.setWindowIcon(
    QIcon(resource_path("assets/logo.ico"))
)

window = MainWindow()
window.show()

sys.exit(app.exec())