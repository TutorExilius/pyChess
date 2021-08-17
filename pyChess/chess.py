from typing import List, Tuple

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget


class Piece:
    def __init__(self, symbol: str, name: str, position: Tuple[int, int]):
        self.symbol: str = symbol
        self.name: str = name
        self._position: Tuple[int, int] = position
        self.move_counter: int = 0
        self.captured: bool = False

    def __repr__(self):
        return self.name

    @property
    def moved_least_once(self) -> bool:
        return self.move_counter > 0

    @property
    def position(self) -> Tuple[int, int]:
        return self._position

    @position.setter
    def position(self, value: Tuple[int, int]):
        if self._position != value:
            self._position = value
            self.move_counter += 1

    def get_color(self) -> str:
        return "black" if "black" in self.name else "white"

    def get_basic_moves(self) -> List[Tuple[int, int]]:
        basic_moves = []
        self_i = self.position[0]
        self_j = self.position[1]

        figure = self.name[: self.name.find("_")]

        if figure == "♟":
            base_row = 1

            if self_i == base_row:
                basic_moves.append((self_i + 2, self_j))

            down_i = self_i + 1
            if down_i <= 7:
                down_left = (down_i, self_j - 1)
                down_right = (down_i, self_j + 1)
                basic_moves.append((down_i, self_j))

                if down_left[1] >= 0:
                    basic_moves.append(down_left)

                if down_right[1] <= 7:
                    basic_moves.append(down_right)

        if figure == "♙":
            base_row = 6

            if self_i == base_row:
                basic_moves.append((self_i - 2, self_j))

            up_i = self_i - 1
            if up_i >= 0:
                up_left = (up_i, self_j - 1)
                up_right = (up_i, self_j + 1)
                basic_moves.append((up_i, self_j))

                if up_left[1] >= 0:
                    basic_moves.append(up_left)

                if up_right[1] <= 7:
                    basic_moves.append(up_right)

        if figure == "♜" or figure == "♖" or figure == "♛" or figure == "♕":
            basic_moves.extend([(i, self_j) for i in range(8) if i != self_i])
            basic_moves.extend([(self_i, j) for j in range(8) if j != self_j])
        if figure == "♝" or figure == "♗" or figure == "♛" or figure == "♕":
            # down right
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
            moves = [
                (self_i + 1, self_j - 2),
                (self_i + 1, self_j + 2),
                (self_i - 1, self_j - 2),
                (self_i - 1, self_j + 2),
                (self_i + 2, self_j - 1),
                (self_i + 2, self_j + 1),
                (self_i - 2, self_j - 1),
                (self_i - 2, self_j + 1),
            ]

            basic_moves.extend([(i, j) for i, j in moves if 0 <= i < 8 and 0 <= j < 8])

        if figure == "♚" or figure == "♔":
            moves = []

            if figure == "♚":
                base_pos = (0, 4)
                if (self_i, self_j) == base_pos:  # castle
                    basic_moves.append((0, 0))
                    basic_moves.append((0, 7))
            else:
                base_pos = (7, 4)
                if (self_i, self_j) == base_pos:  # castle
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

    def __init__(self, position: Tuple[int, int], piece: Piece = None):
        super(Field, self).__init__()

        self.position = position
        self.piece = piece
        self.widget = None
        self.threatened_by: List[Piece] = []

    def update_field(self) -> None:
        new_text = "" if self.piece is None else self.piece.symbol
        self.update_button.emit(new_text)


class Board:
    def __init__(self):
        w, h = 8, 8
        self._board = [[Field(position=(y, x)) for x in range(w)] for y in range(h)]
        self.active_pieces: List[Piece] = []

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
                self.active_pieces.append(piece)

        for i in range(2):
            for j in range(8):
                piece = white_pieces[i * 8 + j]
                self._board[i + 6][j].piece = piece
                self.active_pieces.append(piece)

        self.analyse_threatened_fields()

    def analyse_threatened_fields(self) -> None:
        for piece in self.active_pieces:
            # DEBUG ONLY ---
            if piece.name == "♖_1_white" or piece.name == "♖_2_white":
                print(">>>>>>", len(self.get_possible_moves(piece)))
            # ----

            possible_piece_moves = self.get_possible_moves(piece)

            for threatened_position in possible_piece_moves:
                field = self.get_field(*threatened_position)
                field.threatened_by.append(piece)

    def remove_threat_from_fields_for_piece(self, piece: Piece) -> None:
        possible_piece_moves = self.get_possible_moves(piece)

        for threatened_position in possible_piece_moves:
            field = self.get_field(*threatened_position)
            field.threatened_by.remove(piece)

    def is_collision_free_move(
        self, attacker_piece: Piece, threatened_field: Field
    ) -> bool:
        attacker_piece_i, attacker_piece_j = attacker_piece.position
        threatened_field_i, threatened_field_j = threatened_field.position

        if attacker_piece.symbol in ["♜", "♖"]:
            if attacker_piece_i == threatened_field_i:  # horizontal move
                to_left = attacker_piece_j > threatened_field_j
                _range = (
                    range(attacker_piece_j - 1, threatened_field_j - 1, -1)
                    if to_left
                    else range(attacker_piece_j + 1, threatened_field_j + 1)
                )

                for j in _range:
                    _walking_over_piece = self.get_piece(attacker_piece_i, j)

                    if _walking_over_piece is not None:
                        # check collision

                        if (
                            _walking_over_piece.get_color()
                            == attacker_piece.get_color()
                        ):
                            return False
                        elif j != threatened_field_j:
                            return False

                return True

            else:  # vertical move
                to_up = attacker_piece_i >= threatened_field_i
                _range = (
                    range(attacker_piece_i - 1, threatened_field_i - 1, -1)
                    if to_up
                    else range(attacker_piece_i + 1, threatened_field_i + 1)
                )

                first_enemy_in_row = False
                for i in _range:
                    print("RANGE ---------", list(_range))
                    _walking_over_piece = self.get_piece(i, attacker_piece_j)

                    if _walking_over_piece is not None:
                        if (
                            _walking_over_piece.get_color()
                            == attacker_piece.get_color()
                        ):
                            return False
                        elif (
                            _walking_over_piece.get_color()
                            != attacker_piece.get_color()
                        ):
                            if not first_enemy_in_row:
                                first_enemy_in_row = True
                                print("##### FIRST ")
                                continue
                            else:
                                print("##### SECOND ")
                                return False

                        elif i == threatened_field_i:
                            return True
                        else:
                            return False

                return True

        elif attacker_piece.symbol in ["♝", "♗"]:
            pass
        elif attacker_piece.symbol in ["♞", "♘"]:
            pass
        elif attacker_piece.symbol in ["♛", "♕"]:
            pass
        elif attacker_piece.symbol in ["♚", "♔"]:
            is_castle_move = abs(attacker_piece_j - threatened_field_j) > 1

            if is_castle_move:  # collision check for castle
                # threatened_field has friendly rook to castle with
                if (
                    threatened_field.piece is None
                    or threatened_field.piece.get_color() != attacker_piece.get_color()
                    or threatened_field.piece.moved_least_once
                    or attacker_piece.moved_least_once
                ):
                    return False

                to_left = attacker_piece_j > threatened_field_j
                _range = (
                    range(attacker_piece_j - 1, threatened_field_j, -1)
                    if to_left
                    else range(attacker_piece_j + 1, threatened_field_j)
                )

                # check traversing fields
                for j in _range:
                    crossing_field = self.get_field(attacker_piece_i, j)
                    _threatened_by_enemy = self.threatened_by_enemy(
                        crossing_field, attacker_piece
                    )

                    if _threatened_by_enemy or crossing_field.piece is not None:
                        return False

                return True
            else:  # normal move
                if threatened_field.piece is not None and (
                    threatened_field.piece.get_color() == attacker_piece.get_color()
                ):
                    return False

                if self.threatened_by_enemy(threatened_field, attacker_piece):
                    print(">>>>>>", threatened_field.threatened_by)
                    return False

                return True
        elif attacker_piece.symbol in ["♟", "♙"]:
            pass
        else:
            raise TypeError()

        return False

    @staticmethod
    def threatened_by_enemy(field: Field, piece: Piece) -> bool:
        return any(
            _piece.get_color() != piece.get_color() for _piece in field.threatened_by
        )

    def get_field(self, i: int, j: int) -> Field:
        return self._board[i][j]

    def get_piece(self, i: int, j: int) -> Piece:
        return self._board[i][j].piece

    def get_possible_moves(self, piece: Piece) -> List[Tuple[int, int]]:
        basic_moves = piece.get_basic_moves()
        print(f"Potential moves for {piece.symbol}: {basic_moves}")

        collision_free_moves: List[Tuple[int, int]] = []
        for basic_move in basic_moves:
            field = self.get_field(*basic_move)
            if (
                # piece != other_piece
                # and other_piece.get_color() != piece.get_color()
                # and
                self.is_collision_free_move(piece, field)
            ):
                collision_free_moves.append(basic_move)

        print(f"Collision-Free moves for {piece.symbol}: {collision_free_moves}")

        return collision_free_moves

    def move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> None:
        from_i, from_j = from_pos
        to_i, to_j = to_pos

        from_field = self._board[from_i][from_j]
        to_field = self._board[to_i][to_j]

        from_piece = from_field.piece
        self.remove_threat_from_fields_for_piece(from_piece)

        from_piece.position = to_pos
        to_field.piece = from_piece
        from_field.piece = None

        from_field.update_field()
        to_field.update_field()

        self.analyse_threatened_fields()
