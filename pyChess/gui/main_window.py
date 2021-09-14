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

        self.board = Board()
        self.initialize_new_board()
        self.update_ui()
        self.activated_square = None

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
            ((6, 6), (3, 6)),
            ((6, 1), (0, 1)),
            ((1, 5), (3, 5)),
            # ((2, 1), (3, 1)),
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

        self.activated_square = None
        self.update_ui()

    def update_ui(self) -> None:
        for i in range(8):
            for j in range(8):
                button = self.gridLayout.itemAtPosition(i, j).widget()
                piece = logic.get_piece(self.board, i, j)
                if piece is not None:
                    button.piece = piece
                    button.setText(button.piece.symbol)

                button.update_ui()

        self.listWidget_black.clear()
        self.listWidget_white.clear()

        for piece in logic.get_captured_pieces(self.board, "BLACK"):
            self.listWidget_black.addItem(piece.symbol)

        for piece in logic.get_captured_pieces(self.board, "WHITE"):
            self.listWidget_white.addItem(piece.symbol)

    def on_clicked(self, _, piece_button: QPushButton) -> None:
        # avoid focusing empty squares and pieces qith no move possibilities
        if self.activated_square is None:
            piece = piece_button.square.piece
            possible_moves = logic.get_possible_moves(self.board, piece)

            if not possible_moves:
                return

            # no square focused yet
            self.activated_square = piece_button.square

            for i, j in logic.get_possible_moves(self.board, piece_button.square.piece):
                button = self.gridLayout.itemAtPosition(i, j).widget()
                button.state = States.POSSIBLE_MOVE

                self.update_ui()
        elif piece_button.square == self.activated_square:
            self.reset_highlights()
            self.activated_square = None
        else:
            possible_moves = logic.get_possible_moves(
                self.board, self.activated_square.piece
            )

            if piece_button.square.position in possible_moves:
                self.move_piece(
                    self.activated_square.position, piece_button.square.position
                )
                self.activated_square = None

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
        self.reset_highlights()
