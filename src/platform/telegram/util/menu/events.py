from enum import IntEnum
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.platform.telegram.keyboard.menu import (
    get_main_menu_keyboard,
    get_profile_menu_keyboard,
)
from src.platform.telegram.state.menu import MenuState


class Menu(IntEnum):
    MAIN = 0
    PROFILE = 1
    TRANSACTIONS = 2


async def send_main_menu(text: str, message: Message, state: FSMContext) -> None:
    """
    Reset the current state and send main menu with custom prompt.

    :param text: prompt displayed to the user.
    :type text: str
    :param message: aiogram message
    :type message: Message
    :param state: aiogram FSM context
    :type state: FSMContext
    """
    await state.clear()
    await state.set_state(MenuState.active)
    await state.update_data(current=Menu.MAIN, prev=None)

    await message.answer(text, reply_markup=get_main_menu_keyboard())


async def send_profile_menu(text: str, message: Message, state: FSMContext) -> None:
    await state.update_data(current=Menu.PROFILE, prev=Menu.MAIN)
    await message.answer(text, reply_markup=get_profile_menu_keyboard())


async def send_transactions_menu(
    text: str, message: Message, state: FSMContext
) -> None:
    await state.update_data(current=Menu.TRANSACTIONS, prev=Menu.MAIN)
    await message.answer(text, reply_markup=get_profile_menu_keyboard())
