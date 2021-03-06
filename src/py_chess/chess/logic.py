from copy import deepcopy
from typing import List, Optional, Tuple

from chess.my_types import Board, GameState, Piece, Square, MoveType


def is_collision_free_move(
    board: Board, attacker_piece: Piece, threatened_square: Square
) -> bool:
    return board.is_collision_free_move(attacker_piece, threatened_square)


def threatened_by_enemy(square: Square, piece: Piece) -> bool:
    return Board.threatened_by_enemy(square, piece)


def get_square(board: Board, i: int, j: int) -> Square:
    return board.get_square(i, j)


def get_piece(board: Board, i: int, j: int) -> Optional[Piece]:
    return board.get_piece(i, j)


def get_captured_pieces(board: Board, player_color: str) -> List[Piece]:
    if player_color == "black":
        return [piece for piece in board.player[0].pieces if piece.captured]
    else:
        return [piece for piece in board.player[1].pieces if piece.captured]


def get_active_pieces(board: Board, player_color: str) -> List[Piece]:
    if player_color == "black":
        return [piece for piece in board.player[0].pieces if not piece.captured]
    else:
        return [piece for piece in board.player[1].pieces if not piece.captured]


def get_possible_moves(board: Board, piece: Piece) -> List[Tuple[int, int]]:
    if piece is None:
        return []

    possible_moves = board._get_possible_moves(piece)
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
    else:
        possible_rescuing_moves_for_king = []

        for possible_move in possible_moves:
            cloned_board = deepcopy(board)

            color = piece.get_color()
            king = (
                cloned_board.king_black_piece
                if color == "black"
                else cloned_board.king_white_piece
            )

            king_threatenings = [
                threatener_piece.symbol
                for threatener_piece in cloned_board.get_square(
                    *king.position
                ).threatened_by
                if king.get_color() != threatener_piece.get_color()
            ]

            king_threatenings.sort()

            cloned_board.move(piece.position, possible_move)

            new_king_threatenings = [
                threatener_piece.symbol
                for threatener_piece in cloned_board.get_square(
                    *king.position
                ).threatened_by
                if king.get_color() != threatener_piece.get_color()
            ]

            new_king_threatenings.sort()

            if king_threatenings != new_king_threatenings and new_king_threatenings:
                if len(king_threatenings) > 1:
                    print("Schach matt?")
                    return []

                king_in_check_positions.append(possible_move)
            elif (
                king_threatenings != new_king_threatenings and not new_king_threatenings
            ):
                possible_rescuing_moves_for_king.append(possible_move)
                # return [possible_move]

        if possible_rescuing_moves_for_king:
            return possible_rescuing_moves_for_king

        # simulate only one move and check if own king get into check position/state
        # 1. get current moving color
        # 2. get current list of threatenings of own king
        # 3. one move of possible moves
        # 4. get current list of threatenings of own king
        # 5. compare the two threatening lists
        # 5.1 if different & new list >= 1 -> move leads own king in check state
        # 5.2 is list is equal -> no problemo! :)

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

    if attacker_piece is None:
        raise "Moving piece is None."

    if attacker_piece.symbol in ["♔", "♚"]:
        is_castling_move = abs(attacker_piece_j - threatened_square_j) > 1

        if is_castling_move:
            if board.castling_move_accepted(attacker_piece, threatened_square):
                board.castling_move(from_pos, to_pos)
        else:  # normal move
            board.move(from_pos, to_pos)
    elif attacker_piece.symbol in ["♟", "♙"]:
        is_diagonal_move = attacker_piece_j != threatened_square_j
        is_to_square_free = threatened_square.piece is None

        if is_diagonal_move and is_to_square_free:  # is en passant
            board.en_passant_move(from_pos, to_pos)
        else:
            is_pawn_black = attacker_piece.get_color() == "black"

            if is_pawn_black:
                top_i_line = 7
            else:
                top_i_line = 0

            promotion = None

            if threatened_square_i == top_i_line:  # pawn arrived top line
                promotion = board.open_promotion_piece_dialog(attacker_piece)

            move_type = (
                MoveType.NORMAL_MOVE if promotion is None else MoveType.PROMOTION
            )
            board.move(from_pos, to_pos, move_type, promotion)
    else:
        board.move(from_pos, to_pos)

    if checkmated_kings(board):
        if board.next_move_color == "black":
            return GameState.CHECKMATE_BLACK
        else:
            return GameState.CHECKMATE_WHITE

    return GameState.CONTINUE


def checkmated_kings(board: Board) -> bool:
    # check if one of the kings are in check/mate/checkmate
    if board.next_move_color == "black":
        black_king = board.king_black_piece
        black_king_square = board.get_square(*black_king.position)

        if board.threatened_by_enemy(black_king_square, black_king):
            kings_possible_moves = get_possible_moves(board, black_king)

            if not kings_possible_moves:
                active_black_pieces = get_active_pieces(board, "black")
                can_rescue_the_king = False

                for piece in active_black_pieces:
                    for possible_move in get_possible_moves(board, piece):
                        cloned_board = deepcopy(board)
                        cloned_black_king = cloned_board.king_black_piece
                        cloned_black_king_square = cloned_board.get_square(
                            *cloned_black_king.position
                        )

                        move(cloned_board, piece.position, possible_move)

                        if not cloned_board.threatened_by_enemy(
                            cloned_black_king_square, cloned_black_king
                        ):
                            can_rescue_the_king = True
                            break
                    if can_rescue_the_king:
                        break

                if not can_rescue_the_king:
                    print("Schach matt...")
                    return True
    else:
        white_king = board.king_white_piece
        white_king_square = board.get_square(*white_king.position)

        if board.threatened_by_enemy(white_king_square, white_king):
            kings_possible_moves = get_possible_moves(board, white_king)

            if not kings_possible_moves:
                active_white_pieces = get_active_pieces(board, "white")
                can_rescue_the_king = False

                for piece in active_white_pieces:
                    for possible_move in get_possible_moves(board, piece):
                        cloned_board = deepcopy(board)
                        cloned_white_king = cloned_board.king_white_piece
                        cloned_white_king_square = cloned_board.get_square(
                            *cloned_white_king.position
                        )

                        move(cloned_board, piece.position, possible_move)

                        if not cloned_board.threatened_by_enemy(
                            cloned_white_king_square, cloned_white_king
                        ):
                            can_rescue_the_king = True
                            break
                    if can_rescue_the_king:
                        break

                if not can_rescue_the_king:
                    print("Schach matt...")
                    return True

    return False
