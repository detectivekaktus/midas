from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.loggers import aiogram_logger

from src.util.enums import Currency
from src.usecase.user import RegisterUserUsecase

from src.platform.telegram.validator.currency import valid_currency_filter
from src.platform.telegram.keyboard.currency import get_currency_keyboard
from src.platform.telegram.state.user import UserRegistrationForm
from src.platform.telegram.util.menu.events import send_main_menu


router = Router(name=__name__)


@router.message(Command("start"))
async def handle_start_command(message: Message, state: FSMContext) -> None:
    user = message.from_user
    if not user:
        aiogram_logger.warning("Received `/start` command but couldn't get the user")
        return

    aiogram_logger.info(f"Received `/start` command: {user.id}")

    await state.set_state(UserRegistrationForm.currency)
    await state.update_data(user_id=user.id)
    await message.answer(
        "Hello 👋 Let's start tracking your expenses.\n"
        "What's your preferred currency?",
        reply_markup=get_currency_keyboard(),
    )


@router.message(UserRegistrationForm.currency, valid_currency_filter)
async def handle_currency(
    message: Message, state: FSMContext, currency: Currency
) -> None:
    data = await state.update_data(currency=currency)
    await state.clear()
    aiogram_logger.info(f"Confirmed registration: {data.get("user_id")}")

    try:
        usecase = RegisterUserUsecase()
        await usecase.execute(**data)
        await send_main_menu(message, state, "You've been successfully registered 🥳")
    except KeyError:
        aiogram_logger.warning(
            "Auth middleware malfunction. "
            f"Account creation failed: {data.get("user_id")} is already registered"
        )

        await message.answer(
            "You're already registered 🚫", reply_markup=ReplyKeyboardRemove()
        )


@router.message(UserRegistrationForm.currency)
async def handle_invalid_currency(message: Message) -> None:
    await message.answer(
        "Please, specify a valid currency.", reply_markup=get_currency_keyboard()
    )
