from enum import Enum
from typing import Union

from PyQt5.QtWidgets import QPushButton


class States(Enum):
    NORMAL = 0
    LAST_MOVE = 1
    POSSIBLE_MOVE = 2
    CHECK = 3
    CHECKMATE = 4


class BaseButton(QPushButton):
    def __init__(self) -> None:
        super(BaseButton, self).__init__()

        self.state = States.NORMAL
        self._state_before = self.state
        self.square = None
        self.activated = False
        self.default_style_color = ""
        self.last_move_style_color = ""
        self.possible_move_style_color = ""
        self.check_style_color = ""
        self.checkmate_style_color = ""

    def get_color(self, state: States) -> str:
        if state == States.NORMAL:
            return self.default_style_color
        elif state == States.LAST_MOVE:
            return self.last_move_style_color
        elif state == States.POSSIBLE_MOVE:
            return self.possible_move_style_color
        elif state == States.CHECK:
            return self.check_style_color
        elif state == States.CHECKMATE:
            return self.checkmate_style_color
        else:
            return ""

    def update_ui(self, text: Union[str, None] = None) -> None:
        style = self.styleSheet()
        if self.get_color(self._state_before) in style:
            style = self.styleSheet().replace(
                self.get_color(self._state_before), self.get_color(self.state)
            )
        else:
            style += f" background-color: {self.get_color(self.state)};"

        if text is not None:
            self.setText(text)

        self.setStyleSheet(style)


class BlackButton(BaseButton):
    def __init__(self) -> None:
        super(BlackButton, self).__init__()

        self.default_style_color = "#cccccc"
        self.last_move_style_color = "#ccccee"
        self.possible_move_style_color = "#ffc0c0"
        self.check_style_color = "#ffcccc"
        self.checkmate_style_color = "#ffbbbb"

        self.update_ui()


class WhiteButton(BaseButton):
    def __init__(self) -> None:
        super(WhiteButton, self).__init__()

        self.default_style_color = "#ffffff"
        self.last_move_style_color = "#f0f0ff"
        self.possible_move_style_color = "#ffc0c0"
        self.check_style_color = "#ffeeee"
        self.checkmate_style_color = "#ffdddd"

        self.update_ui()
