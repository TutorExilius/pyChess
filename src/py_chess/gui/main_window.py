import time
from functools import partial
from pathlib import Path
from typing import Dict, Tuple

from chess import logic
from chess.my_types import Board, GameState
from gui.my_widgets import BlackButton, States, WhiteButton
from gui.promotion_piece_dialog import PromotionPieceDialog
from PyQt5 import uic
from PyQt5.QtCore import QCoreApplication, Qt  # , QTimer
from PyQt5.QtWidgets import QLabel, QLayout, QMainWindow, QPushButton, QMessageBox


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()

        self.ui = uic.loadUi(Path(__file__).parent / "ui" / "main_window.ui", self)
        self.board = None
        self.initialize_game()

        # connections
        self.pushButton_reset_game.clicked.connect(self.initialize_game)

    def initialize_game(self) -> None:
        self.initialize_new_board()
        self.activated_square = None
        self.pushButton_reset_game.setVisible(False)

        # s = 3000
        # print(f"Start Simulation in {s / 1000} seconds...")
        # QTimer.singleShot(s, partial(self.on_simulation_start, 0.0))

    @staticmethod
    def _clearlayout(layout: QLayout) -> None:
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            layout.removeItem(item)
            item.widget().deleteLater()

    def on_simulation_start(self, interval_in_sec: int) -> None:
        # Debug only ---
        moves = [
            ((7, 7), (5, 7)),
            ((1, 3), (2, 3)),
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
            ((1, 1), (7, 1)),
        ]

        for _move in moves:
            from_pos, to_pos = _move
            self.move_piece(from_pos, to_pos)
            self.update_ui()

            QCoreApplication.processEvents()
            time.sleep(interval_in_sec)

        # self.initialize_new_board()

    def reset_highlights(self) -> None:
        for i in range(1, 9):
            for j in range(1, 9):
                button = self.gridLayout_board.itemAtPosition(i, j).widget()
                button.state = States.NORMAL

        self.activated_square = None
        self.update_ui()

    def update_ui(self) -> None:
        for i in range(1, 9):
            for j in range(1, 9):
                button = self.gridLayout_board.itemAtPosition(i, j).widget()
                piece = logic.get_piece(self.board, i - 1, j - 1)
                if piece is not None:
                    button.piece = piece
                    button.setText(button.piece.symbol)

                button.update_ui()

        for i, piece in enumerate(logic.get_captured_pieces(self.board, "black")):
            label = self.gridLayout_black.itemAtPosition(i, 0).widget()
            label.setText(piece.symbol)

        for i, piece in enumerate(logic.get_captured_pieces(self.board, "white")):
            label = self.gridLayout_white.itemAtPosition(i, 0).widget()
            label.setText(piece.symbol)

    def on_clicked(self, _: bool, piece_button: QPushButton) -> None:
        if self.board is None or self.board.game_over:
            return

        piece = piece_button.square.piece

        # avoid focusing empty squares and pieces with no move possibilities
        if self.activated_square is None:
            possible_moves = logic.get_possible_moves(self.board, piece)

            if not possible_moves:
                return

            # piece is not none, so the color can be requested here
            if self.board.next_move_color != piece.get_color():
                print("Not your turn! Next move:", self.board.next_move_color)
                return

            # no square focused yet
            self.activated_square = piece_button.square

            for i, j in logic.get_possible_moves(self.board, piece_button.square.piece):
                button = self.gridLayout_board.itemAtPosition(i + 1, j + 1).widget()
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

        if self.board and self.board.kings_in_check:
            print("king in check")
            # TODO: neue (noch nicht) implementierte Methode in board benutzen,
            #  dass eine Liste von möglichen bewegbaren Figuren und deren mölichen
            #  Züge zurückliefert, die dazu führen die Schachsituation des Königs
            #  aufzuheben. -> einschließlich die Zugmöglichkeiten des Königs,
            #  die ihn aus dem Schach holen

    def initialize_new_board(self) -> None:
        def callback_dialog(transformable_piece_symbols: Dict[str, str]) -> str:
            dialog = PromotionPieceDialog(self, transformable_piece_symbols)
            dialog.exec()

            symbol = PromotionPieceDialog.selected_piece_symbol
            PromotionPieceDialog.selected_piece_symbol = ""

            return symbol

        if self.board is not None:
            del self.board

        self.board = Board(callback_dialog)

        # --- reset states
        MainWindow._clearlayout(self.gridLayout_black)
        MainWindow._clearlayout(self.gridLayout_white)
        MainWindow._clearlayout(self.gridLayout_board)

        self.activated_square = None
        # ---

        for _ in range(15):
            label_1 = QLabel()
            label_1.setStyleSheet("font-size: 30px;")
            label_1.setAlignment(Qt.AlignCenter)

            label_2 = QLabel()
            label_2.setStyleSheet("font-size: 30px;")
            label_2.setAlignment(Qt.AlignCenter)

            self.gridLayout_black.addWidget(label_1)
            self.gridLayout_white.addWidget(label_2)

        def set_button_text(button: QPushButton, button_text: str) -> None:
            button.setText(button_text)

        FACTOR = 60
        SIZE = f"width: {FACTOR + 10}px; height: {FACTOR + 10}px;"

        # corner
        label_1 = QLabel()
        label_2 = QLabel()
        label_3 = QLabel()
        label_4 = QLabel()
        style = (
            f"width: {FACTOR / 2}px; height: {FACTOR / 2}px;"
            "background: #777; color: white;"
        )
        label_1.setStyleSheet(style)
        label_2.setStyleSheet(style)
        label_3.setStyleSheet(style)
        label_4.setStyleSheet(style)

        self.gridLayout_board.addWidget(label_1, 0, 0)
        self.gridLayout_board.addWidget(label_2, 0, 10)
        self.gridLayout_board.addWidget(label_3, 10, 0)
        self.gridLayout_board.addWidget(label_4, 10, 10)

        # set frame labels
        # top & bottom frames
        for j in range(8):
            text = chr(ord("A") + j)

            label_1 = QLabel()
            label_1.setStyleSheet(
                f"width: {FACTOR}px; height: {FACTOR / 2}px;"
                "font-size: 16px; font-weight: bold; padding: 5px 0px 5px;"
                # "border: 1px solid #999;"
                "background: #777; color: white;"
            )
            label_1.setAlignment(Qt.AlignCenter)
            label_1.setText(text)

            label_2 = QLabel()
            label_2.setStyleSheet(
                f"width: {FACTOR}px; height: {FACTOR / 2}px;"
                "font-size: 16px; font-weight: bold; padding: 5px 0px 5px;"
                # "border: 1px solid #999;"
                "background: #777; color: white;"
            )
            label_2.setAlignment(Qt.AlignCenter)
            label_2.setText(text)

            self.gridLayout_board.addWidget(label_1, 0, j + 1)
            self.gridLayout_board.addWidget(label_2, 10, j + 1)

        # left & right frames
        for i in range(8):
            text = str(9 - (i + 1))

            label_1 = QLabel()
            label_1.setStyleSheet(
                f"width: {FACTOR / 2}px; height: {FACTOR}px;"
                "font-size: 16px; font-weight: bold; padding: 0px 12px 0px 12px;"
                # "border: 1px solid #999;"
                "background: #777; color: white;"
            )
            label_1.setAlignment(Qt.AlignCenter)
            label_1.setText(text)

            label_2 = QLabel()
            label_2.setStyleSheet(
                f"width: {FACTOR / 2}px; height: {FACTOR}px;"
                "font-size: 16px; font-weight: bold; padding: 0px 12px 0px 12px;"
                # "border: 1px solid #999;"
                "background: #777; color: white;"
            )
            label_2.setAlignment(Qt.AlignCenter)
            label_2.setText(text)

            self.gridLayout_board.addWidget(label_1, i + 1, 0)
            self.gridLayout_board.addWidget(label_2, i + 1, 10)

        for i in range(1, 9):
            for j in range(1, 9):
                white = (i - 1 + j - 1) % 2 == 0

                button = WhiteButton() if white else BlackButton()
                button.setStyleSheet(f"{SIZE} font-size: {FACTOR / 2}pt;")

                self.gridLayout_board.addWidget(button, i, j)

                square = logic.get_square(self.board, i - 1, j - 1)
                button.square = square

                square.callback_dialog = partial(set_button_text, button)
                button.clicked.connect(partial(self.on_clicked, False, button))

        self.reset_highlights()
        self.setFixedSize(self.sizeHint())

    def move_piece(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> None:
        move_result = logic.move(self.board, from_pos, to_pos)

        if move_result != GameState.CONTINUE:
            msg_box = QMessageBox(self)
            msg_box_title = "Game Over"

            if move_result == GameState.CHECKMATE_BLACK:
                msg_box_text = "WHITE won"
                print("White won")
            elif move_result == GameState.CHECKMATE_WHITE:
                msg_box_text = "BLACK won"
                print("Black won")
            elif move_result == GameState.REMIS:
                msg_box_text = "Remis."
                print("Remis")
            else:
                raise TypeError(f"Move Return Type '{move_result}' is unknown")

            self.reset_highlights()

            msg_box.setText(msg_box_text)
            msg_box.setStyleSheet("width: 100px; height: 30px;")
            msg_box.setWindowTitle(msg_box_title)
            msg_box.exec()

            if self.board is not None:
                self.board.game_over = True
                self.pushButton_reset_game.setVisible(self.board.game_over)
        else:
            self.reset_highlights()
