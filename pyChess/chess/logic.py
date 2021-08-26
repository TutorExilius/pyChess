from typing import List, Tuple

from copy import deepcopy

from pyChess.chess.my_types import Board, Field, Piece


def analyse_threatened_fields(board: Board) -> None:
    board.analyse_threatened_fields()


def remove_threat_from_fields(board: Board) -> None:
    board.remove_threat_from_fields()


def is_collision_free_move(
    board: Board, attacker_piece: Piece, threatened_field: Field
) -> bool:
    return board.is_collision_free_move(attacker_piece, threatened_field)


def threatened_by_enemy(field: Field, piece: Piece) -> bool:
    return Board.threatened_by_enemy(field, piece)


def get_field(board: Board, i: int, j: int) -> Field:
    return board.get_field(i, j)


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
            to_field = cloned_board.get_field(pos_i, pos_j)

            if cloned_board.threatened_by_enemy(to_field, piece):
                king_in_check_positions.append(possible_move)

    return [
        possible_move
        for possible_move in possible_moves
        if possible_move not in king_in_check_positions
    ]


def move(board: Board, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> None:
    board.move(from_pos, to_pos)
