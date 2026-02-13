from aiogram.fsm.state import State, StatesGroup

from midas.platform.telegram.util.rendering import PagerStatesGroup


class TransactionForm(StatesGroup):
    """
    Transaction form.
    """

    title = State()
    transaction_type = State()
    description = State()
    amount = State()


class TransactionPaginationState(PagerStatesGroup):
    pass
