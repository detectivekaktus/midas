from aiogram.fsm.state import State, StatesGroup


class TransactionForm(StatesGroup):
    """
    Transaction form.
    """

    title = State()
    transaction_type = State()
    description = State()
    amount = State()


class TransactionPaginationState(StatesGroup):
    show = State()
    confirm_delete = State()
