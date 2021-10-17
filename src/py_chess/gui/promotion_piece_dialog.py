from pathlib import Path
from typing import Dict
from functools import partial

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QWidget


class PromotionPieceDialog(QDialog):
    selected_piece_symbol = ""

    def __init__(
        self, parent: QWidget, transformable_piece_symbols: Dict[str, str]
    ) -> None:
        super(PromotionPieceDialog, self).__init__(parent=parent)

        uic.loadUi(Path(__file__).parent / "ui" / "promotion_piece_dialog.ui", self)

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setStyleSheet("QDialog{border: 2px outset grey; background-color: white}")
        self.label_description.setStyleSheet("background-color: white")

        piece_button_style = (
            "QPushButton:hover:!pressed"
            "{"
            "   border: 2px outset black;"
            "   background-color: white;"
            "}"
            "QPushButton"
            "{"
            "   border: 1px solid black;"
            "   background-color: white;"
            "}"
        )

        self.pushButton_queen.setText(transformable_piece_symbols["queen"])
        self.pushButton_queen.setStyleSheet(piece_button_style)
        self.pushButton_rook.setText(transformable_piece_symbols["rook"])
        self.pushButton_rook.setStyleSheet(piece_button_style)
        self.pushButton_bishop.setText(transformable_piece_symbols["bishop"])
        self.pushButton_bishop.setStyleSheet(piece_button_style)
        self.pushButton_knight.setText(transformable_piece_symbols["knight"])
        self.pushButton_knight.setStyleSheet(piece_button_style)

        # connections
        self.pushButton_queen.clicked.connect(
            partial(self.on_piece_clicked, False, self.pushButton_queen.text())
        )
        self.pushButton_rook.clicked.connect(
            partial(self.on_piece_clicked, False, self.pushButton_rook.text())
        )
        self.pushButton_bishop.clicked.connect(
            partial(self.on_piece_clicked, False, self.pushButton_bishop.text())
        )
        self.pushButton_knight.clicked.connect(
            partial(self.on_piece_clicked, False, self.pushButton_knight.text())
        )

    def on_piece_clicked(self, _: bool, symbol: str) -> None:
        PromotionPieceDialog.selected_piece_symbol = symbol
        self.close()
