from aiogram.fsm.state import State, StatesGroup


class EventForm(StatesGroup):
    """
    Event form.
    """

    title = State()
    transaction_type = State()
    description = State()
    amount = State()
    frequency = State()
