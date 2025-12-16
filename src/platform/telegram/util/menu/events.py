from enum import IntEnum
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from src.platform.telegram.keyboard.menu import (
    get_main_menu_keyboard,
    get_profile_menu_keyboard,
    get_transactions_menu_keyboard,
)
from src.platform.telegram.state.menu import MenuState


class Menu(IntEnum):
    MAIN = 0
    PROFILE = 1
    TRANSACTIONS = 2


async def send_main_menu(
    message: Message,
    state: FSMContext,
    text: str = "Select an option from list below.",
    reset_state: bool = True,
) -> None:
    """
    Reset the current state and send main menu with custom prompt.

    :param text: prompt displayed to the user.
    :type text: str
    :param message: aiogram message
    :type message: Message
    :param state: aiogram FSM context
    :type state: FSMContext
    """
    if reset_state:
        await state.clear()
        await state.set_state(MenuState.active)
    await state.update_data(current=Menu.MAIN, prev=None)

    await message.answer(text, reply_markup=get_main_menu_keyboard())


async def send_profile_menu(
    message: Message, state: FSMContext, text: str = "Select an option from list below."
) -> None:
    await state.update_data(current=Menu.PROFILE, prev=Menu.MAIN)
    await message.answer(text, reply_markup=get_profile_menu_keyboard())


async def send_transactions_menu(
    message: Message, state: FSMContext, text: str = "Select an option from list below."
) -> None:
    await state.update_data(current=Menu.TRANSACTIONS, prev=Menu.MAIN)
    await message.answer(text, reply_markup=get_transactions_menu_keyboard())


async def remove_menu(message: Message, state: FSMContext) -> None:
    """
    Remove previously attached menu.

    Calling this function resets the state and removes the reply markup.

    :param message: aiogram message
    :type message: Message
    :param state: aiogram FSM context
    :type state: FSMContext
    """
    await state.clear()
    await message.answer("Wait...", reply_markup=ReplyKeyboardRemove())
