from pathlib import Path
import random

from PyQt5 import uic
from PyQt5.QtCore import QDir, QRegExp, Qt
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QWidget


class ReplayManager(QMainWindow):
    def __init__(self, parent: QWidget) -> None:
        super(ReplayManager, self).__init__(parent=parent)

        self.game_window = parent

        self.ui = uic.loadUi(Path(__file__).parent / "ui" / "replay_manager.ui", self)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, False)
        self.lineEdit_delay_in_sec.setAlignment(Qt.AlignCenter)

        # sounds
        self.select_all_sounds = ["media/doubleclick_select_all_1.wav"]

        # validators
        delay_in_sec_validator = QRegExpValidator(
            QRegExp("[+]?([0-9]+(?:[\\.][0-9]{0,3})?|\\.[0-9]{0,3})")
        )
        self.lineEdit_delay_in_sec.setValidator(delay_in_sec_validator)

        # connection
        self.pushButton_replay.clicked.connect(self.simulate_game)
        self.pushButton_load_file.clicked.connect(self.open_txt_file)
        self.listWidget.itemDoubleClicked.connect(lambda _: self.select_all())

    def open_txt_file(self) -> None:
        filename = QFileDialog.getOpenFileName(
            self, "Open Document", QDir.currentPath(), "text files (*.txt)"
        )[0]

        self.lineEdit.setText(filename)

        with open(filename, encoding="utf8") as f:
            lines = f.read().split("\n")

        for line in lines:
            self.listWidget.addItem(line)

        self.listWidget.selectAll()

    def simulate_game(self) -> None:
        # board = self.game_window.board
        delay = float(self.lineEdit_delay_in_sec.text())
        print(f"Delay: {delay} sec")

        items = self.listWidget.selectedItems()
        x = []
        for i in range(len(items)):
            x.append(str(self.listWidget.selectedItems()[i].text()))

        print(x)

    def select_all(self) -> None:
        self.listWidget.selectAll()

        selected_sound = random.choice(self.select_all_sounds)
        sound_path_str = str(Path(__file__).parent.parent / selected_sound)

        print("play sound:", sound_path_str)
        QSound.play(sound_path_str)
