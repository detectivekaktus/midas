from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from midas.service.user_caching import CachedUser
from midas.usecase.storage import GetUserStorageUsecase
from midas.util.enums import Currency

from midas.platform.telegram.state.menu import MenuState
from midas.platform.telegram.util.menu.events import (
    Menu,
    send_events_menu,
    send_main_menu,
    send_profile_menu,
    send_transactions_menu,
)
from midas.platform.telegram.util.menu.options import BackOption, MainMenuOption


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


@router.message(MenuState.active, F.text == MainMenuOption.EVENTS)
async def handle_events_menu(message: Message, state: FSMContext) -> None:
    await send_events_menu(message, state)


@router.message(Command("balance"))
@router.message(MenuState.active, F.text == MainMenuOption.BALANCE)
async def handle_balance_command(
    message: Message, state: FSMContext, user: CachedUser
) -> None:
    usecase = GetUserStorageUsecase()
    storage = await usecase.execute(user.id)

    currency = Currency(user.currency_id).name
    text = f"🏦 Your current balance: {currency} {storage.amount}"
    await send_main_menu(message, state, text=text)


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
