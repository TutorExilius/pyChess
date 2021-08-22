from typing import List, Tuple
from copy import deepcopy

from pyChess.chess.types import Board, Field, Piece


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
    remove_moves = []

    if piece.symbol in ["♚", "♔"]:
        # TODO: copy board, remove signal/slot connections
        #  and move in all kings possible fields to detect checks
        #  if done, romve them from list 'possible_moves'

        board.block_signals(True)

        cloned_board = deepcopy(board)
        king_field = cloned_board.get_field(**Piece.position)
        king_field.blockSignals(True)

        for possible_move in possible_moves:
            move_field = cloned_board.get_field(*possible_move)
            move_field.blockSignals(True)

            cloned_board.move(**king_field.position, **move_field.position)

            if len(king_field.threatened_by) > 0:
                remove_moves.append(possible_move)

        board.block_signals(False)
    return possible_moves - remove_moves


def move(board: Board, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> None:
    board.move(from_pos, to_pos)
