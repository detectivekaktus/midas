from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.loggers import aiogram_logger
from src.service.user_caching import CachedUser

from src.util.enums import Currency
from src.usecase.user import RegisterUserUsecase, EditUserUsecase

from src.platform.telegram.validator.currency import valid_currency_filter
from src.platform.telegram.keyboard.currency import get_currency_keyboard
from src.platform.telegram.state import FormMode
from src.platform.telegram.state.user import UserForm
from src.platform.telegram.util.menu.events import remove_menu, send_main_menu
from src.platform.telegram.util.menu.options import ProfileMenuOption


router = Router(name=__name__)


async def register_user(message: Message, state: FSMContext) -> None:
    data = {k: v for k, v in (await state.get_data()).items() if k not in ("mode")}
    await state.clear()

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


async def change_user_currency(message: Message, state: FSMContext) -> None:
    data = {k: v for k, v in (await state.get_data()).items() if k not in ("mode")}
    await state.clear()

    try:
        usecase = EditUserUsecase()
        await usecase.execute(**data)
        await send_main_menu(
            message, state, f"Currency changed to {data.get("currency").name}."  # type: ignore
        )
    except ValueError:
        aiogram_logger.error(f"User currency change failed: {data.get("user_id")}")
        await send_main_menu(message, state, "Failed. Something wrong happened.")


@router.message(Command("start"))
async def handle_start_command(message: Message, state: FSMContext) -> None:
    user = message.from_user
    if user is None:
        aiogram_logger.warning("Received `/start` command but couldn't get the user")
        return

    aiogram_logger.info(f"Received `/start` command: {user.id}")

    await state.set_state(UserForm.currency)
    await state.update_data(user_id=user.id, mode=FormMode.CREATE)
    await message.answer(
        "Hello 👋 Let's start tracking your expenses.\n"
        "What's your preferred currency?",
        reply_markup=get_currency_keyboard(),
    )


@router.message(Command("edit_profile"))
@router.message(F.text == ProfileMenuOption.CHANGE_PROFILE)
async def handle_edit_profile_command(
    message: Message, state: FSMContext, user: CachedUser
) -> None:
    aiogram_logger.info(f"Received `/edit_profile` command: {user.id}")

    await remove_menu(message, state)

    mode = FormMode.EDIT
    await state.update_data(user_id=user.id, mode=mode)
    await state.set_state(UserForm.currency)
    await message.answer("Select new currency.", reply_markup=get_currency_keyboard())


@router.message(UserForm.currency, valid_currency_filter)
async def handle_currency(
    message: Message, state: FSMContext, currency: Currency
) -> None:
    mode = await state.get_value("mode")
    await state.update_data(currency=currency)

    if mode == FormMode.CREATE:
        aiogram_logger.info(
            f"Confirmed registration: {await state.get_value("user_id")}"
        )
        await register_user(message, state)
    else:
        aiogram_logger.info(
            f"Confirmed currency change: {await state.get_value("user_id")}"
        )
        await change_user_currency(message, state)


@router.message(UserForm.currency)
async def handle_invalid_currency(message: Message) -> None:
    await message.answer(
        "Please, specify a valid currency.", reply_markup=get_currency_keyboard()
    )
