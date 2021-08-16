from functools import partial
from pathlib import Path
from typing import Tuple
import time

from PyQt5.QtCore import QTimer, QCoreApplication
from PyQt5.QtWidgets import QMainWindow, QPushButton
from PyQt5 import uic

from my_widgets import BlackButton, WhiteButton, States
from chess import Board


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        uic.loadUi(Path(__file__).parent / "ui" / "main_window.ui", self)

        self._focused_piece_button = None
        self.board = Board()
        self.initialize_new_board()
        self.update_ui()

        s = 3000
        print(f"Start Simulation in {s/1000} seconds...")
        QTimer.singleShot(s, partial(self.on_simulation_start, 0.1))

    def on_simulation_start(self, intervall_in_sec):
        # Debug only ---
        # self.move_piece((0, 0), (2, 0))

        moves = [
            ((1, 3), (2, 3)),
            ((7, 7), (5, 7)),
            ((6, 5), (5, 5)),
            ((7, 1), (5, 1)),
            ((7, 2), (5, 2)),
            ((7, 4), (5, 4)),
            ((2, 3), (4, 3)),
            ((0, 1), (2, 1)),
            ((0, 2), (2, 2)),
            ((0, 3), (2, 4)),
            ((0, 4), (0, 3)),
            ((0, 3), (0, 4)),
            ((0, 0), (0, 1)),
            ((0, 1), (0, 0)),
            # ((7, 0), (2, 3)),
        ]

        for _move in moves:
            from_pos, to_pos = _move
            print(from_pos, "->", to_pos)
            self.move_piece(from_pos, to_pos)
            self.update_ui()

            QCoreApplication.processEvents()
            time.sleep(intervall_in_sec)

    def reset_highlights(self) -> None:
        for i in range(8):
            for j in range(8):
                button = self.gridLayout.itemAtPosition(i, j).widget()
                button.state = States.NORMAL

    def update_ui(self) -> None:
        for i in range(8):
            for j in range(8):
                button = self.gridLayout.itemAtPosition(i, j).widget()
                piece = self.board.get_piece(i, j)
                if piece is not None:
                    button.piece = piece
                    button.setText(button.piece.symbol)

                button.update_ui()

    def on_clicked(self, _, piece_button: QPushButton) -> None:
        piece = piece_button.field.piece
        if piece is not None:

            self.reset_highlights()

            if piece_button != self._focused_piece_button:
                for i, j in self.board.get_possible_moves(piece):
                    button = self.gridLayout.itemAtPosition(i, j).widget()
                    button.state = States.POSSIBLE_MOVE
                self._focused_piece_button = piece_button
            else:
                self._focused_piece_button = None

            self.update_ui()

    def initialize_new_board(self) -> None:
        if self.board is None:
            self.board = Board()

        for i in range(8):
            for j in range(8):
                white = (i + j) % 2 == 0

                factor = 60
                size = f"width: {factor}px; height: {factor}px;"

                button = WhiteButton() if white else BlackButton()
                button.setStyleSheet(f"{size} font-size: {factor/2}pt;")

                self.gridLayout.addWidget(button, i, j)

                field = self.board.get_field(i, j)
                field.widget = button
                button.field = field
                field.update_button.connect(button.update_ui)
                button.clicked.connect(partial(self.on_clicked, False, button))

        self.update_ui()
        self.setFixedSize(self.sizeHint())

    def reset_board(self) -> None:
        self.board = Board()

    def move_piece(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> None:
        self.board.move(from_pos, to_pos)
