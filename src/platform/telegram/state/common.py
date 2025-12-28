from enum import IntEnum
from aiogram.fsm.state import State, StatesGroup


class ConfirmForm(StatesGroup):
    confirm = State()


class FormMode(IntEnum):
    CREATE = 0
    EDIT = 1
