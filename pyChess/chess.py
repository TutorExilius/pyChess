from typing import List, Tuple
from dataclasses import dataclass

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget


@dataclass
class Piece:
    symbol: str
    name: str
    position: Tuple[int, int]

    def get_basic_moves(self) -> List[Tuple[int, int]]:
        basic_moves = []
        self_i = self.position[0]
        self_j = self.position[1]

        figure = self.name[: self.name.find("_")]  # king

        if figure == "♟":
            base_row = 1
            basic_moves.append((self_i + 1, self_j))

            if self_i == base_row:
                basic_moves.append((self_i + 2, self_j))
        if figure == "♙":
            base_row = 6
            basic_moves.append((self_i - 1, self_j))

            if self_i == base_row:
                basic_moves.append((self_i - 2, self_j))
        if figure == "♜" or figure == "♖" or figure == "♛" or figure == "♕":
            basic_moves.extend([(i, self_j) for i in range(8) if i != self_i])
            basic_moves.extend([(self_i, j) for j in range(8) if j != self_j])
        if figure == "♝" or figure == "♗" or figure == "♛" or figure == "♕":
            # bottom right
            i = self_i
            j = self_j

            while True:
                i += 1
                j += 1

                if i > 7 or j > 7:
                    break

                basic_moves.append((i, j))

            # up right
            i = self_i
            j = self_j

            while True:
                i -= 1
                j += 1

                if i < 0 or j > 7:
                    break

                basic_moves.append((i, j))

            # down left
            i = self_i
            j = self_j

            while True:
                i += 1
                j -= 1

                if i > 7 or j < 0:
                    break

                basic_moves.append((i, j))

            # up left
            i = self_i
            j = self_j

            while True:
                i -= 1
                j -= 1

                if i < 0 or j < 0:
                    break

                basic_moves.append((i, j))

        if figure == "♞" or figure == "♘":
            moves = []
            moves.append((self_i + 1, self_j - 2))
            moves.append((self_i + 1, self_j + 2))

            moves.append((self_i - 1, self_j - 2))
            moves.append((self_i - 1, self_j + 2))

            moves.append((self_i + 2, self_j - 1))
            moves.append((self_i + 2, self_j + 1))

            moves.append((self_i - 2, self_j - 1))
            moves.append((self_i - 2, self_j + 1))

            basic_moves.extend([(i, j) for i, j in moves if 0 <= i < 8 and 0 <= j < 8])

        if figure == "♚" or figure == "♔":
            moves = []

            if figure == "♚":
                base_pos = (0, 4)
                if (self_i, self_j) == base_pos:  # rochade
                    basic_moves.append((0, 0))
                    basic_moves.append((0, 7))
            else:
                base_pos = (7, 4)
                if (self_i, self_j) == base_pos:  # rochade
                    basic_moves.append((7, 0))
                    basic_moves.append((7, 7))

            moves.append((self_i - 1, self_j))
            moves.append((self_i + 1, self_j))
            moves.append((self_i, self_j - 1))
            moves.append((self_i, self_j + 1))
            moves.append((self_i + 1, self_j + 1))
            moves.append((self_i + 1, self_j - 1))
            moves.append((self_i - 1, self_j + 1))
            moves.append((self_i - 1, self_j - 1))

            basic_moves.extend([(i, j) for i, j in moves if 0 <= i < 8 and 0 <= j < 8])

        return basic_moves


class Field(QWidget):
    update_button = pyqtSignal(str)

    def __init__(self, piece: Piece = None):
        super(Field, self).__init__()

        self.piece = piece
        self.widget = None

    def update_field(self) -> None:
        new_text = "" if self.piece is None else self.piece.symbol
        self.update_button.emit(new_text)


class Board:
    def __init__(self):
        w, h = 8, 8
        self._board = [[Field() for x in range(w)] for y in range(h)]

        black_pieces = [
            Piece(symbol="♜", name="♜_1_black", position=(0, 0)),
            Piece(symbol="♞", name="♞_1_black", position=(0, 1)),
            Piece(symbol="♝", name="♝_1_black", position=(0, 2)),
            Piece(symbol="♛", name="♛_1_black", position=(0, 3)),
            Piece(symbol="♚", name="♚_1_black", position=(0, 4)),
            Piece(symbol="♝", name="♝_2_black", position=(0, 5)),
            Piece(symbol="♞", name="♞_2_black", position=(0, 6)),
            Piece(symbol="♜", name="♜_2_black", position=(0, 7)),
            Piece(symbol="♟", name="♟_1_black", position=(1, 0)),
            Piece(symbol="♟", name="♟_2_black", position=(1, 1)),
            Piece(symbol="♟", name="♟_3_black", position=(1, 2)),
            Piece(symbol="♟", name="♟_4_black", position=(1, 3)),
            Piece(symbol="♟", name="♟_5_black", position=(1, 4)),
            Piece(symbol="♟", name="♟_6_black", position=(1, 5)),
            Piece(symbol="♟", name="♟_7_black", position=(1, 6)),
            Piece(symbol="♟", name="♟_8_black", position=(1, 7)),
        ]

        white_pieces = [
            Piece(symbol="♙", name="♙_1_white", position=(6, 0)),
            Piece(symbol="♙", name="♙_2_white", position=(6, 1)),
            Piece(symbol="♙", name="♙_3_white", position=(6, 2)),
            Piece(symbol="♙", name="♙_4_white", position=(6, 3)),
            Piece(symbol="♙", name="♙_5_white", position=(6, 4)),
            Piece(symbol="♙", name="♙_6_white", position=(6, 5)),
            Piece(symbol="♙", name="♙_7_white", position=(6, 6)),
            Piece(symbol="♙", name="♙_8_white", position=(6, 7)),
            Piece(symbol="♖", name="♖_1_white", position=(7, 0)),
            Piece(symbol="♘", name="♘_1_white", position=(7, 1)),
            Piece(symbol="♗", name="♗_1_white", position=(7, 2)),
            Piece(symbol="♕", name="♕_1_white", position=(7, 3)),
            Piece(symbol="♔", name="♔_1_white", position=(7, 4)),
            Piece(symbol="♗", name="♗_2_white", position=(7, 5)),
            Piece(symbol="♘", name="♘_2_white", position=(7, 6)),
            Piece(symbol="♖", name="♖_2_white", position=(7, 7)),
        ]

        for i in range(2):
            for j in range(8):
                piece = black_pieces[i * 8 + j]
                self._board[i][j].piece = piece

        for i in range(2):
            for j in range(8):
                piece = white_pieces[i * 8 + j]
                self._board[i + 6][j].piece = piece

    def get_field(self, i: int, j: int) -> Field:
        return self._board[i][j]

    def get_piece(self, i: int, j: int) -> Piece:
        return self._board[i][j].piece

    def move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> None:
        from_i, from_j = from_pos
        to_i, to_j = to_pos

        from_field = self._board[from_i][from_j]
        to_field = self._board[to_i][to_j]

        piece = from_field.piece
        piece.position = to_pos
        to_field.piece = piece
        from_field.piece = None

        from_field.update_field()
        to_field.update_field()
