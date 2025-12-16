from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.platform.telegram.state.menu import MenuState
from src.platform.telegram.util.menu.events import (
    Menu,
    send_main_menu,
    send_profile_menu,
    send_transactions_menu,
)
from src.platform.telegram.util.menu.options import BackOption, MainMenuOption


router = Router(name=__name__)


@router.message(Command("menu"))
async def handle_menu_command(message: Message, state: FSMContext) -> None:
    await send_main_menu(message, state)


@router.message(MenuState.active, F.text == MainMenuOption.PROFILE)
async def handle_profile_menu(message: Message, state: FSMContext) -> None:
    await send_profile_menu(message, state)


@router.message(MenuState.active, F.text == MainMenuOption.TRANSACTIONS)
async def handle_transactions_menu(message: Message, state: FSMContext) -> None:
    await send_transactions_menu(message, state)


@router.message(MenuState.active, F.text == BackOption.BACK)
async def handle_go_back_menu(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    current: Menu = data["current"]
    prev: Menu = data["prev"]

    if prev is None or current == Menu.MAIN:
        await message.answer("You can't go back from main menu.")
        return

    match prev:
        case Menu.MAIN:
            await send_main_menu(message, state, reset_state=False)
        case _:
            await send_main_menu(message, state, reset_state=False)


@router.message(MenuState.active)
async def handle_invalid_menu(message: Message) -> None:
    await message.answer("Please, select an option from the list.")
