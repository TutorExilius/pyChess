import sys

from PyQt5.QtWidgets import QApplication

from gui.main_window import MainWindow


def main() -> int:
    app = QApplication([])

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec_() or 0)


if __name__ == "__main__":
    main()
