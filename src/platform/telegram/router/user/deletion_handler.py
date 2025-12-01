from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.loggers import aiogram_logger

from src.usecase.user import DeleteUserUsecase

from src.platform.telegram.validator import YesNoAnswer
from src.platform.telegram.keyboard import get_yes_no_keyboard
from src.platform.telegram.state import ConfirmForm


router = Router(name=__name__)


@router.message(Command("delete_profile"))
async def handle_delete_profile(message: Message, state: FSMContext) -> None:
    user = message.from_user
    if not user:
        aiogram_logger.warning(
            "Received `/delete_profile` command but couldn't get the user"
        )
        return

    aiogram_logger.info(f"Received `/delete_profile` command: {user.id}")

    await state.set_state(ConfirmForm.confirm)
    await state.update_data(user_id=user.id)
    await message.answer(
        "Are you sure you want to delete your profile?\n"
        "This action will delete all your history, storages,"
        " and accounts.",
        reply_markup=get_yes_no_keyboard(),
    )


@router.message(ConfirmForm.confirm, F.text == YesNoAnswer.NO)
async def handle_reject_profile_deletion(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Cancelled profile deletion.", reply_markup=ReplyKeyboardRemove()
    )


@router.message(ConfirmForm.confirm, F.text == YesNoAnswer.YES)
async def handle_confirm_profile_deletion(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()
    aiogram_logger.info(f"Confirmed account deletion: {data.get("user_id")}")

    try:
        usecase = DeleteUserUsecase()
        await usecase.execute(**data)
        await message.answer(
            "Your profile has been deleted 😭", reply_markup=ReplyKeyboardRemove()
        )
    except ValueError:
        aiogram_logger.warning(
            "Auth middleware malfunction. "
            f"Account deletion failed: {data.get("user_id")} is not registered"
        )

        await message.answer(
            "You are not registered 🚫", reply_markup=ReplyKeyboardRemove()
        )


@router.message(ConfirmForm.confirm)
async def handle_invalid_option(message: Message) -> None:
    await message.answer(
        "Please, select an option from a list below.",
        reply_markup=get_yes_no_keyboard(),
    )
