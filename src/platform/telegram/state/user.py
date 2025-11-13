from aiogram.fsm.state import State, StatesGroup


class UserRegistrationForm(StatesGroup):
    """
    User registration form.

    This form contains the user's preferred currency
    that'll be added to the database.
    """

    currency = State()
