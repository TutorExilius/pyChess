import random
import time
from pathlib import Path
from typing import List, Tuple

from chess.my_types import MoveType
from PyQt5 import uic
from PyQt5.QtCore import QCoreApplication, QDir, QRegExp, Qt
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QWidget


class ReplayManager(QMainWindow):
    def __init__(self, parent: QWidget) -> None:
        super(ReplayManager, self).__init__(parent=parent)

        self.game_window = parent

        self.ui = uic.loadUi(Path(__file__).parent / "ui" / "replay_manager.ui", self)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, False)
        self.lineEdit_delay_in_sec.setAlignment(Qt.AlignCenter)

        # sounds
        self.select_all_sounds = [
            "media/doubleclick_select_all_1.wav",
            "media/doubleclick_select_all_2.wav",
            "media/doubleclick_select_all_3.wav",
        ]

        # validators
        delay_in_sec_validator = QRegExpValidator(
            QRegExp("[+]?([0-9]+(?:[\\.][0-9]{0,3})?|\\.[0-9]{0,3})")
        )
        self.lineEdit_delay_in_sec.setValidator(delay_in_sec_validator)

        # connection
        self.pushButton_replay.clicked.connect(self.simulate_game)
        self.pushButton_load_file.clicked.connect(self.open_txt_file)
        self.listWidget.itemDoubleClicked.connect(lambda _: self.select_all())

    def open_txt_file(self) -> None:
        filename = QFileDialog.getOpenFileName(
            self, "Open Document", QDir.currentPath(), "text files (*.txt)"
        )[0]

        if not filename:
            return

        self.lineEdit.setText(filename)

        with open(filename, encoding="utf8") as f:
            lines = f.read().split("\n")

        for line in lines:
            self.listWidget.addItem(line)

        self.listWidget.selectAll()

    def simulate_game(self) -> None:
        board = self.game_window.board
        delay = float(self.lineEdit_delay_in_sec.text())
        print(f"Delay: {delay} sec")

        items = self.listWidget.selectedItems()
        chess_notations = [item.text() for item in items]

        print(chess_notations)

        for chess_notation in chess_notations:
            # replace all " e.p." to"_e.p." to avoid to be splitted in
            #  parse_notation(..) -> string.split(" ")
            while " e.p." in chess_notation:
                chess_notation = chess_notation.replace(" e.p.", "_e.p.")

            print("Move:", chess_notation)
            promotions, moves = self.parse_notation(chess_notation)

            for i, move in enumerate(moves):
                time.sleep(delay)

                from_pos, to_pos, move_type = move
                promotion = promotions[i]

                if move_type == MoveType.NORMAL_MOVE:
                    board.move(from_pos, to_pos, move_type, promotion)
                elif move_type == MoveType.EN_PASSANT:
                    board.en_passant_move(from_pos, to_pos)
                elif move_type == MoveType.CASTLING_MOVE:
                    board.castling_move(from_pos, to_pos)
                else:
                    raise TypeError("Move Type unknown.")

                self.game_window.update_ui()
                QCoreApplication.processEvents()

    def parse_notation(
        self, chess_notation: str
    ) -> Tuple[List[str], List[Tuple[Tuple[int, int], Tuple[int, int]]]]:
        move_parts = chess_notation.split(" ")
        move_parts = move_parts[1:]
        return self._parse_move(move_parts)

    def _parse_move(
        self, move_notation: List[str]
    ) -> Tuple[List[str], List[Tuple[Tuple[int, int], Tuple[int, int]]]]:
        rows = {"1": 0, "2": 1, "3": 2, "4": 3, "5": 4, "6": 5, "7": 6, "8": 7}
        cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}

        possible_seperators = ["–", "x", "×"]
        possible_promotion_postfixes = ["Q", "B", "N", "R"]
        castling_notations = ["0–0", "0–0–0"]

        white_move = move_notation[0]
        black_move = move_notation[1] if len(move_notation) > 1 else None

        white_castling = False
        black_castling = False

        is_white_en_passant = False
        is_black_en_passant = False

        white_promoted_piece = None
        black_promoted_piece = None

        if white_move not in castling_notations:
            white_from_pos, white_to_pos = white_move.split(
                self.use_seperator(white_move, possible_seperators)
            )
            white_from_pos = self.remove_piece_prefix(white_from_pos)
            white_to_pos = self.remove_piece_prefix(white_to_pos)
            is_white_en_passant, white_to_pos = self.remove_en_passant_postfix(
                white_to_pos
            )

            if any(postfix in white_to_pos for postfix in possible_promotion_postfixes):
                white_promoted_piece = white_to_pos[-1]
        else:
            white_castling = True

        if black_move is not None:
            if black_move not in castling_notations:
                black_from_pos, black_to_pos = black_move.split(
                    self.use_seperator(black_move, possible_seperators)
                )
                black_from_pos = self.remove_piece_prefix(black_from_pos)
                black_to_pos = self.remove_piece_prefix(black_to_pos)
                is_black_en_passant, black_to_pos = self.remove_en_passant_postfix(
                    black_to_pos
                )

                if any(
                    postfix in black_to_pos for postfix in possible_promotion_postfixes
                ):
                    black_promoted_piece = black_to_pos[-1]
            else:
                black_castling = True

        moves = []

        # white
        if white_castling:
            if white_move == "0–0":  # short castling
                moves.append(
                    (
                        (7, 4),  # from_pos
                        (7, 7),  # to_pos
                        MoveType.CASTLING_MOVE,
                    )
                )
            else:  # long castling
                moves.append(
                    (
                        (7, 4),  # from_pos
                        (7, 0),  # to_pos
                        MoveType.CASTLING_MOVE,
                    )
                )
        else:
            moves.append(
                (
                    (rows[white_from_pos[1]], cols[white_from_pos[0]]),  # from_pos
                    (rows[white_to_pos[1]], cols[white_to_pos[0]]),  # to_pos
                    MoveType.EN_PASSANT
                    if is_white_en_passant
                    else MoveType.NORMAL_MOVE,
                )
            )

        # black
        if black_move is not None:
            if black_castling:
                if black_move == "0–0":  # short castling
                    moves.append(
                        (
                            (0, 4),  # from_pos
                            (0, 7),  # to_pos
                            MoveType.CASTLING_MOVE,
                        )
                    )
                else:  # long castling
                    moves.append(
                        (
                            (0, 4),  # from_pos
                            (0, 0),  # to_pos
                            MoveType.CASTLING_MOVE,
                        )
                    )
            else:
                moves.append(
                    (
                        (rows[black_from_pos[1]], cols[black_from_pos[0]]),  # from_pos
                        (rows[black_to_pos[1]], cols[black_to_pos[0]]),  # to_pos
                        MoveType.EN_PASSANT
                        if is_black_en_passant
                        else MoveType.NORMAL_MOVE,
                    )
                )

        return [white_promoted_piece, black_promoted_piece], moves

    def remove_piece_prefix(self, move_notation: str) -> str:
        return move_notation[1:] if move_notation[0].isupper() else move_notation

    def remove_en_passant_postfix(self, move_notation: str) -> Tuple[bool, str]:
        en_passant_found = move_notation.endswith("_e.p.")
        return en_passant_found, move_notation.removesuffix("_e.p.")

    def use_seperator(self, move_notation: str, possible_seperators: List[str]) -> str:
        for sep in possible_seperators:
            if sep in move_notation:
                return sep

        raise ValueError("No seperator in notation found.")

    def select_all(self) -> None:
        self.listWidget.selectAll()

        selected_sound = random.choice(self.select_all_sounds)
        sound_path_str = str(Path(__file__).parent.parent / selected_sound)

        print("play sound:", sound_path_str)
        QSound.play(sound_path_str)
