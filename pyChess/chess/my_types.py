from typing import List, Set, Tuple
from copy import deepcopy

# from PyQt5.QtCore import pyqtSignal, QObject


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

        if figure in ["♜", "♖", "♛", "♕"]:
            basic_moves.extend([(i, self_j) for i in range(8) if i != self_i])
            basic_moves.extend([(self_i, j) for j in range(8) if j != self_j])

        if figure in ["♝", "♗", "♛", "♕"]:
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

        if figure in ["♞", "♘"]:
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

        if figure in ["♚", "♔"]:
            moves = []

            if figure == "♚":
                base_pos = (0, 4)
                if (self_i, self_j) == base_pos:  # castling
                    basic_moves.append((0, 0))
                    basic_moves.append((0, 7))
            else:
                base_pos = (7, 4)
                if (self_i, self_j) == base_pos:  # castling
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


class Square:
    def __init__(
        self, position: Tuple[int, int], piece: Piece = None, ui_callback=None
    ):
        self.ui_callback = ui_callback
        self.position = position
        self.piece = piece
        self.threatened_by: Set[Piece] = set()

    def __deepcopy__(self, memodict={}):
        cls = self.__class__
        result = cls.__new__(cls)
        memodict[id(self)] = result
        for k, v in self.__dict__.items():
            if k == "ui_callback":
                setattr(result, k, None)
            elif k == "threatened_by":
                setattr(result, k, [])
            else:
                setattr(result, k, deepcopy(v, memodict))
        return result

    def update_square(self) -> None:
        if self.ui_callback is not None:
            new_text = "" if self.piece is None else self.piece.symbol
            self.ui_callback(new_text)


class Board:
    def __init__(self):
        w, h = 8, 8
        self._board = [[Square(position=(i, j)) for j in range(w)] for i in range(h)]
        self.active_pieces: List[Piece] = []
        self.last_moves: List[Tuple[Square, Square]] = []

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

        self.analyse_threatened_squares()

    def __deepcopy__(self, memodict={}):
        cls = self.__class__
        result = cls.__new__(cls)
        memodict[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memodict))
        return result

    def analyse_threatened_squares(self) -> None:
        for piece in self.active_pieces:
            possible_piece_moves = self.get_possible_moves(piece)
            print(f"{piece.name}: possible: {possible_piece_moves}")

            for threatened_position in possible_piece_moves:
                square = self.get_square(*threatened_position)
                square.threatened_by.add(piece)

    def remove_threat_from_squares(self) -> None:
        for i in range(0, 8):
            for j in range(0, 8):
                square = self.get_square(i, j)
                square.threatened_by = set()

    def _is_diagonal_move_collision_free(
        self,
        attacker_piece_i,
        attacker_piece_j,
        threatened_square_i,
        threatened_square_j,
        attacker_piece,
    ):
        # top
        if threatened_square_i < attacker_piece_i:
            # left
            if threatened_square_j < attacker_piece_j:
                for i, j in zip(
                    range(attacker_piece_i - 1, threatened_square_i - 1, -1),
                    range(attacker_piece_j - 1, threatened_square_j - 1, -1),
                ):
                    _walking_over_piece = self.get_piece(i, j)

                    if _walking_over_piece is not None:
                        # check collision

                        if (
                            _walking_over_piece.get_color()
                            == attacker_piece.get_color()
                        ):
                            return False
                        elif i == threatened_square_i and j == threatened_square_j:
                            return True
                        else:
                            return False
            # right
            else:
                for i, j in zip(
                    range(attacker_piece_i - 1, threatened_square_i - 1, -1),
                    range(attacker_piece_j + 1, threatened_square_j + 1),
                ):
                    _walking_over_piece = self.get_piece(i, j)

                    if _walking_over_piece is not None:
                        # check collision

                        if (
                            _walking_over_piece.get_color()
                            == attacker_piece.get_color()
                        ):
                            return False
                        elif i == threatened_square_i and j == threatened_square_j:
                            return True
                        else:
                            return False
        # down
        else:
            # left
            if threatened_square_j < attacker_piece_j:
                for i, j in zip(
                    range(attacker_piece_i + 1, threatened_square_i + 1),
                    range(attacker_piece_j - 1, threatened_square_j - 1, -1),
                ):
                    _walking_over_piece = self.get_piece(i, j)

                    if _walking_over_piece is not None:
                        # check collision

                        if (
                            _walking_over_piece.get_color()
                            == attacker_piece.get_color()
                        ):
                            return False
                        elif i == threatened_square_i and j == threatened_square_j:
                            return True
                        else:
                            return False
            # right
            else:
                for i, j in zip(
                    range(attacker_piece_i + 1, threatened_square_i + 1),
                    range(attacker_piece_j + 1, threatened_square_j + 1),
                ):
                    _walking_over_piece = self.get_piece(i, j)

                    if _walking_over_piece is not None:
                        # check collision

                        if (
                            _walking_over_piece.get_color()
                            == attacker_piece.get_color()
                        ):
                            return False
                        elif i == threatened_square_i and j == threatened_square_j:
                            return True
                        else:
                            return False
        return True

    def _is_straight_move_collision_free(
        self,
        attacker_piece_i,
        attacker_piece_j,
        threatened_square_i,
        threatened_square_j,
        attacker_piece,
    ):
        if attacker_piece_i == threatened_square_i:  # horizontal move
            to_left = attacker_piece_j >= threatened_square_j
            _range = (
                range(attacker_piece_j - 1, threatened_square_j - 1, -1)
                if to_left
                else range(attacker_piece_j + 1, threatened_square_j + 1)
            )

            for j in _range:
                _walking_over_piece = self.get_piece(attacker_piece_i, j)

                if _walking_over_piece is not None:
                    # check collision

                    if _walking_over_piece.get_color() == attacker_piece.get_color():
                        return False
                    elif j == threatened_square_j:
                        return True
                    else:
                        return False

            return True

        else:  # vertical move
            to_up = attacker_piece_i >= threatened_square_i
            _range = (
                range(attacker_piece_i - 1, threatened_square_i - 1, -1)
                if to_up
                else range(attacker_piece_i + 1, threatened_square_i + 1)
            )

            for i in _range:
                _walking_over_piece = self.get_piece(i, attacker_piece_j)

                if _walking_over_piece is not None:
                    if _walking_over_piece.get_color() == attacker_piece.get_color():
                        return False
                    elif i == threatened_square_i:
                        return True
                    else:
                        return False

            return True

    def is_collision_free_move(
        self, attacker_piece: Piece, threatened_square: Square
    ) -> bool:
        attacker_piece_i, attacker_piece_j = attacker_piece.position
        threatened_square_i, threatened_square_j = threatened_square.position

        if attacker_piece.symbol in ["♜", "♖"]:
            return self._is_straight_move_collision_free(
                attacker_piece_i,
                attacker_piece_j,
                threatened_square_i,
                threatened_square_j,
                attacker_piece,
            )
        elif attacker_piece.symbol in ["♝", "♗"]:
            return self._is_diagonal_move_collision_free(
                attacker_piece_i,
                attacker_piece_j,
                threatened_square_i,
                threatened_square_j,
                attacker_piece,
            )
        elif attacker_piece.symbol in ["♞", "♘"]:
            if (
                threatened_square.piece is not None
                and threatened_square.piece.get_color() == attacker_piece.get_color()
            ):
                return False

            return True
        elif attacker_piece.symbol in ["♛", "♕"]:
            is_straight_move = (
                threatened_square_i == attacker_piece_i
                or threatened_square_j == attacker_piece_j
            )

            if is_straight_move:
                return self._is_straight_move_collision_free(
                    attacker_piece_i,
                    attacker_piece_j,
                    threatened_square_i,
                    threatened_square_j,
                    attacker_piece,
                )
            else:
                return self._is_diagonal_move_collision_free(
                    attacker_piece_i,
                    attacker_piece_j,
                    threatened_square_i,
                    threatened_square_j,
                    attacker_piece,
                )
        elif attacker_piece.symbol in ["♚", "♔"]:
            is_castling_move = abs(attacker_piece_j - threatened_square_j) > 1

            if is_castling_move:  # collision check for castling
                # threatened_square has friendly rook to castling with
                if (
                    threatened_square.piece is None
                    or threatened_square.piece.get_color() != attacker_piece.get_color()
                    or threatened_square.piece.moved_least_once
                    or attacker_piece.moved_least_once
                ):
                    return False

                to_left = attacker_piece_j > threatened_square_j
                _range = (
                    range(attacker_piece_j - 1, threatened_square_j, -1)
                    if to_left
                    else range(attacker_piece_j + 1, threatened_square_j)
                )

                # check traversing squares
                for j in _range:
                    crossing_square = self.get_square(attacker_piece_i, j)
                    _threatened_by_enemy = self.threatened_by_enemy(
                        crossing_square, attacker_piece
                    )

                    if _threatened_by_enemy or crossing_square.piece is not None:
                        return False

                return True
            else:  # normal move
                if threatened_square.piece is not None and (
                    threatened_square.piece.get_color() == attacker_piece.get_color()
                ):
                    return False

                if self.threatened_by_enemy(threatened_square, attacker_piece):
                    return False

                return True
        elif attacker_piece.symbol in ["♟", "♙"]:
            is_diagonal = attacker_piece_j != threatened_square_j

            if is_diagonal:
                is_diagonal_enemy = (
                    threatened_square.piece is not None
                    and threatened_square.piece.get_color()
                    != attacker_piece.get_color()
                )

                if not is_diagonal_enemy:
                    if not self.last_moves:
                        return False

                    last_from_square, last_to_square = self.last_moves[-1]
                    last_move_piece = last_to_square.piece

                    was_to_step_opening = (
                        abs(last_from_square.position[0] - last_to_square.position[0])
                        == 2
                    )

                    is_last_pawn_enemy_move = False
                    next_to_attacker = False

                    if last_move_piece:
                        is_last_pawn_enemy_move = (
                            last_move_piece.get_color() != attacker_piece.get_color()
                        )
                        next_to_attacker = (
                            abs(attacker_piece_j - last_move_piece.position[1]) == 1
                        )
                        behind_to_last_move_piece = (
                            abs(last_move_piece.position[0] - threatened_square_i) == 1
                        ) and last_move_piece.position[1] == threatened_square_j

                    if (
                        is_last_pawn_enemy_move
                        and was_to_step_opening
                        and next_to_attacker
                        and behind_to_last_move_piece
                    ):
                        return True
                else:
                    return True
            else:
                if abs(threatened_square_i - attacker_piece_i) == 2:  # two step opening
                    in_front_i = (
                        attacker_piece_i + 1
                        if attacker_piece.get_color() == "black"
                        else attacker_piece_i - 1
                    )

                    if 0 <= in_front_i <= 7:
                        in_front_is_free = (
                            self.get_piece(in_front_i, attacker_piece_j) is None
                        )

                        if threatened_square.piece is None and in_front_is_free:
                            return True
                else:
                    return threatened_square.piece is None
        else:
            raise TypeError()

        return False

    @staticmethod
    def threatened_by_enemy(square: Square, piece: Piece) -> bool:
        return any(
            _piece.get_color() != piece.get_color() for _piece in square.threatened_by
        )

    def get_square(self, i: int, j: int) -> Square:
        return self._board[i][j]

    def get_piece(self, i: int, j: int) -> Piece:
        return self._board[i][j].piece

    def get_possible_moves(self, piece: Piece) -> List[Tuple[int, int]]:
        basic_moves = piece.get_basic_moves()

        collision_free_moves: List[Tuple[int, int]] = []
        for basic_move in basic_moves:
            square = self.get_square(*basic_move)
            if (
                # piece != other_piece
                # and other_piece.get_color() != piece.get_color()
                # and
                self.is_collision_free_move(piece, square)
            ):
                collision_free_moves.append(basic_move)

        return collision_free_moves

    def move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> None:
        from_i, from_j = from_pos
        to_i, to_j = to_pos

        from_square = self._board[from_i][from_j]
        to_square = self._board[to_i][to_j]

        from_piece = from_square.piece
        self.remove_threat_from_squares()

        from_piece.position = to_pos
        to_square.piece = from_piece
        from_square.piece = None

        from_square.update_square()
        to_square.update_square()

        self.last_moves.append((from_square, to_square))
        self.analyse_threatened_squares()
