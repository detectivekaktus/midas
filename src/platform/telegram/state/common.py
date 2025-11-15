from aiogram.fsm.state import State, StatesGroup


class ConfirmForm(StatesGroup):
    confirm = State()