from typing import List, Tuple

from copy import deepcopy

from pyChess.chess.my_types import Board, Square, Piece


def reinitialize_threatenings(board: Board) -> None:
    board.reinitialize_threatenings()


def remove_threat_from_squares(board: Board) -> None:
    board.remove_threat_from_squares()


def is_collision_free_move(
    board: Board, attacker_piece: Piece, threatened_square: Square
) -> bool:
    return board.is_collision_free_move(attacker_piece, threatened_square)


def threatened_by_enemy(square: Square, piece: Piece) -> bool:
    return Board.threatened_by_enemy(square, piece)


def get_square(board: Board, i: int, j: int) -> Square:
    return board.get_square(i, j)


def get_piece(board: Board, i: int, j: int) -> Piece:
    return board.get_piece(i, j)


def get_captured_pieces(board: Board, player_color: str) -> List[Piece]:
    if player_color == "BLACK":
        return [piece for piece in board.player[0].pieces if piece.captured]
    else:
        return [piece for piece in board.player[1].pieces if piece.captured]


def get_possible_moves(board: Board, piece: Piece) -> List[Tuple[int, int]]:
    if piece is None:
        return []

    possible_moves = board.get_possible_moves(piece)
    king_in_check_positions: List[Tuple[int, int]] = []

    if piece.symbol in ["♚", "♔"]:
        king_pos = piece.position
        king_pos_i, king_pos_j = king_pos

        for possible_move in possible_moves:
            is_castling_move = abs(king_pos_j - possible_move[1]) > 1

            if not is_castling_move:
                cloned_board = deepcopy(board)
                cloned_board.move(king_pos, possible_move)
                pos_i, pos_j = possible_move
                to_square = cloned_board.get_square(pos_i, pos_j)

                if cloned_board.threatened_by_enemy(to_square, piece):
                    king_in_check_positions.append(possible_move)

    return [
        possible_move
        for possible_move in possible_moves
        if possible_move not in king_in_check_positions
    ]


def move(board: Board, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> None:
    attacker_piece_i, attacker_piece_j = from_pos
    threatened_square_i, threatened_square_j = to_pos

    attacker_piece = board.get_piece(attacker_piece_i, attacker_piece_j)
    threatened_square = board.get_square(threatened_square_i, threatened_square_j)

    if attacker_piece.symbol in ["♔", "♚"]:
        is_castling_move = abs(attacker_piece_j - threatened_square_j) > 1

        if is_castling_move:
            if castling_move_accepted(board, attacker_piece, threatened_square):
                board.castling_move(from_pos, to_pos)
        else:  # normal move
            board.move(from_pos, to_pos)
    else:
        board.move(from_pos, to_pos)


def castling_move_accepted(
    board: Board, attacker_piece: Piece, threatened_square: Square
) -> bool:
    if threatened_square.piece is None:
        return False

    attacker_piece_i, attacker_piece_j = attacker_piece.position
    threatened_square_i, threatened_square_j = threatened_square.piece.position

    # threatened_square has friendly rook to castling with
    if (
        threatened_square.piece.get_color() != attacker_piece.get_color()
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
    for step, j in enumerate(_range, start=1):
        crossing_square = board.get_square(attacker_piece_i, j)

        if crossing_square.piece is not None:
            return False

        if step < 3:
            _threatened_by_enemy = board.threatened_by_enemy(
                crossing_square, attacker_piece
            )

            if _threatened_by_enemy:
                return False

    return True
