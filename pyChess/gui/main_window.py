import time
from functools import partial
from pathlib import Path
from typing import Tuple

from PyQt5 import uic
from PyQt5.QtCore import QCoreApplication, QTimer
from PyQt5.QtWidgets import QMainWindow, QPushButton

from pyChess.chess import logic
from pyChess.chess.my_types import Board
from pyChess.gui.my_widgets import BlackButton, States, WhiteButton


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        uic.loadUi(Path(__file__).parent / "ui" / "main_window.ui", self)

        self._focused_piece_button = None
        self.board = Board()
        self.initialize_new_board()
        self.update_ui()

        s = 3000
        print(f"Start Simulation in {s / 1000} seconds...")
        QTimer.singleShot(s, partial(self.on_simulation_start, 0))

    def on_simulation_start(self, interval_in_sec: int) -> None:
        # Debug only ---
        moves = [
            ((1, 3), (2, 3)),
            ((7, 7), (5, 7)),
            ((6, 5), (5, 5)),
            ((7, 1), (5, 1)),
            ((7, 2), (5, 2)),
            ((7, 3), (7, 7)),
            ((2, 3), (4, 3)),
            ((0, 1), (2, 1)),
            ((0, 2), (2, 2)),
            ((0, 3), (2, 4)),
            ((0, 4), (3, 7)),
            # ((0, 3), (0, 4)),
            # ((0, 0), (0, 1)),
            # ((0, 1), (0, 0)),
            # ((0, 4), (4, 5)),
            ((7, 6), (4, 4)),
            ((6, 6), (4, 6)),
            ((6, 1), (0, 1)),
            # ((3, 7), (4, 6)),
        ]

        for _move in moves:
            from_pos, to_pos = _move
            self.move_piece(from_pos, to_pos)
            self.update_ui()

            QCoreApplication.processEvents()
            time.sleep(interval_in_sec)

    def reset_highlights(self) -> None:
        for i in range(8):
            for j in range(8):
                button = self.gridLayout.itemAtPosition(i, j).widget()
                button.state = States.NORMAL

    def update_ui(self) -> None:
        for i in range(8):
            for j in range(8):
                button = self.gridLayout.itemAtPosition(i, j).widget()
                piece = logic.get_piece(self.board, i, j)
                if piece is not None:
                    button.piece = piece
                    button.setText(button.piece.symbol)

                button.update_ui()

    def on_clicked(self, _, piece_button: QPushButton) -> None:
        piece = piece_button.square.piece
        print(
            f"square {piece_button.square.position} - "
            f"Threatened by {piece_button.square.threatened_by}"
        )
        if piece is not None:
            self.reset_highlights()

            if piece_button != self._focused_piece_button:
                for i, j in logic.get_possible_moves(self.board, piece):
                    button = self.gridLayout.itemAtPosition(i, j).widget()
                    button.state = States.POSSIBLE_MOVE
                self._focused_piece_button = piece_button
            else:
                self._focused_piece_button = None

            self.update_ui()

    def initialize_new_board(self) -> None:
        def set_button_text(button, button_text):
            button.setText(button_text)

        if self.board is None:
            self.board = Board()

        for i in range(8):
            for j in range(8):
                white = (i + j) % 2 == 0

                factor = 60
                size = f"width: {factor}px; height: {factor}px;"

                button = WhiteButton() if white else BlackButton()
                button.setStyleSheet(f"{size} font-size: {factor / 2}pt;")

                self.gridLayout.addWidget(button, i, j)

                square = logic.get_square(self.board, i, j)
                button.square = square

                square.ui_callback = partial(set_button_text, button)
                button.clicked.connect(partial(self.on_clicked, False, button))

        self.update_ui()
        self.setFixedSize(self.sizeHint())

    def reset_board(self) -> None:
        self.board = Board()

    def move_piece(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> None:
        logic.move(self.board, from_pos, to_pos)
