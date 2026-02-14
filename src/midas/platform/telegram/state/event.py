from aiogram.fsm.state import State, StatesGroup

from midas.platform.telegram.util.rendering import PagerStatesGroup


class EventForm(StatesGroup):
    """
    Event form.
    """

    title = State()
    transaction_type = State()
    description = State()
    amount = State()
    frequency = State()


class EventPaginationState(PagerStatesGroup):
    show = State()
    confirm_delete = State()
