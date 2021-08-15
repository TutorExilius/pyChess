from functools import partial
from pathlib import Path

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

        self._initialize_grid_layout()
        self.update_ui()

        self.move_piece((0, 0), (2, 0))
        self.move_piece((1, 3), (2, 3))
        self.move_piece((7, 7), (5, 7))
        self.move_piece((6, 5), (5, 5))
        self.move_piece((7, 1), (5, 1))
        self.move_piece((7, 2), (5, 2))

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
                    piece.field = button
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

    def _initialize_grid_layout(self) -> None:
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
                button.update_ui()

        self.setFixedSize(self.sizeHint())

    def reset_board(self) -> None:
        self.board = Board()

    def move_piece(self, from_pos: int, to_pos: int) -> None:
        self.board.move(from_pos, to_pos)
