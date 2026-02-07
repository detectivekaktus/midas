from typing import Optional
from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from midas.loggers import aiogram_logger
from midas.service.user_caching import CachedUser

from midas.usecase.user import RegisterUserUsecase, EditUserUsecase
from midas.util.enums import Currency
from midas.util.errors import NoChangesDetectedException

from midas.platform.telegram.validator import SkipAnswer, YesNoAnswer
from midas.platform.telegram.validator.currency import valid_currency_filter
from midas.platform.telegram.keyboard import get_yes_no_keyboard
from midas.platform.telegram.keyboard.currency import get_currency_keyboard
from midas.platform.telegram.router.util import skipped_unskippable
from midas.platform.telegram.state import FormMode
from midas.platform.telegram.state.user import UserForm
from midas.platform.telegram.util.menu.events import remove_menu, send_main_menu
from midas.platform.telegram.util.menu.options import ProfileMenuOption


router = Router(name=__name__)


async def register_user(message: Message, state: FSMContext) -> None:
    data = {k: v for k, v in (await state.get_data()).items() if k not in ("mode")}

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


async def edit_user(message: Message, state: FSMContext) -> None:
    data = {k: v for k, v in (await state.get_data()).items() if k not in ("mode")}

    try:
        usecase = EditUserUsecase()
        await usecase.execute(**data)
        await send_main_menu(message, state, f"Successfully edited profile.")
    except NoChangesDetectedException:
        await send_main_menu(message, state, "No changes detected.")
        return
    except Exception:
        aiogram_logger.error(f"User edit failed: {data.get("user_id")}")
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
    await message.answer(
        "Select new currency.", reply_markup=get_currency_keyboard(skippable=True)
    )


@router.message(UserForm.currency, valid_currency_filter)
@router.message(UserForm.currency, F.text == SkipAnswer.SKIP)
async def handle_currency(
    message: Message, state: FSMContext, currency: Optional[Currency] = None
) -> None:
    mode: FormMode = await state.get_value("mode")  # type: ignore
    if await skipped_unskippable(
        message, mode, currency, get_currency_keyboard(skippable=True)
    ):
        return

    if mode == FormMode.CREATE:
        await state.update_data(currency=currency)
        aiogram_logger.info(
            f"Confirmed registration: {await state.get_value("user_id")}"
        )
        await register_user(message, state)
    else:
        if currency is not None and message.text != SkipAnswer.SKIP:
            await state.update_data(currency=currency)

        await message.answer(
            "Would you like to get notifications?", reply_markup=get_yes_no_keyboard()
        )
        await state.set_state(UserForm.notifications)


@router.message(UserForm.currency)
async def handle_invalid_currency(message: Message, state: FSMContext) -> None:
    await message.answer(
        "Please, specify a valid currency.",
        reply_markup=get_currency_keyboard(
            skippable=await state.get_value("mode") == FormMode.EDIT
        ),
    )


@router.message(UserForm.notifications, F.text == YesNoAnswer.YES)
@router.message(UserForm.notifications, F.text == YesNoAnswer.NO)
async def handle_notifications(message: Message, state: FSMContext) -> None:
    mode = await state.get_value("mode")

    if mode == FormMode.EDIT:
        send_notifications = message.text == YesNoAnswer.YES
        await state.update_data(send_notifications=send_notifications)

        aiogram_logger.info(
            f"Confirmed profile edit: {await state.get_value("user_id")}"
        )
        await edit_user(message, state)


@router.message(UserForm.notifications)
async def handle_invalid_notifications(message: Message) -> None:
    await message.answer(
        "Please, select an option from down below.", reply_markup=get_yes_no_keyboard()
    )
