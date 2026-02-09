#internal
import sys

# external
from PySide6.QtWidgets import QApplication

# private
from main_window import MainWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())
