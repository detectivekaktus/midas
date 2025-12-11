from typing import Literal
from aiogram.fsm.state import State, StatesGroup


class ConfirmForm(StatesGroup):
    confirm = State()


FormMode = Literal["create", "edit"]
