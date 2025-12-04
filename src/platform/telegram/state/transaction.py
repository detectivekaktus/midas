from aiogram.fsm.state import State, StatesGroup


class CreateTransactionForm(StatesGroup):
    """
    Create transaction form.

    This form contains all essential data for creating
    a transaction required for `CreateTransactionUsecase`
    class.
    """

    user_id = State()
    title = State()
    transaction_type = State()
    description = State()
    amount = State()


class TransactionPaginationState(StatesGroup):
    show = State()
