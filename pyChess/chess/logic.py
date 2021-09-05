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


def get_possible_moves(board: Board, piece: Piece) -> List[Tuple[int, int]]:
    possible_moves = board.get_possible_moves(piece)
    king_in_check_positions: List[Tuple[int, int]] = []

    if piece.symbol in ["♚", "♔"]:
        king_pos = piece.position

        for possible_move in possible_moves:
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
    board.move(from_pos, to_pos)
