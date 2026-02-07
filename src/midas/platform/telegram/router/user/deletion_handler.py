from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from midas.loggers import aiogram_logger
from midas.service.user_caching import CachedUser
from midas.services import user_storage

from midas.usecase.user import DeleteUserUsecase

from midas.platform.telegram.validator import YesNoAnswer
from midas.platform.telegram.keyboard import get_yes_no_keyboard
from midas.platform.telegram.state import ConfirmForm
from midas.platform.telegram.util.menu.events import remove_menu
from midas.platform.telegram.util.menu.options import ProfileMenuOption


router = Router(name=__name__)


@router.message(Command("delete_profile"))
@router.message(F.text == ProfileMenuOption.DELETE_PROFILE)
async def handle_delete_profile(
    message: Message, state: FSMContext, user: CachedUser
) -> None:
    aiogram_logger.info(f"Received `/delete_profile` command: {user.id}")

    await remove_menu(message, state)

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
    user_id: int = data["user_id"]

    await state.clear()
    aiogram_logger.info(f"Confirmed account deletion: {user_id}")

    try:
        if await user_storage.exists(user_id):
            await user_storage.delete(user_id)

        usecase = DeleteUserUsecase()
        await usecase.execute(user_id)
        await message.answer(
            "Your profile has been deleted 😭", reply_markup=ReplyKeyboardRemove()
        )
    except ValueError:
        aiogram_logger.warning(
            "Auth middleware malfunction. "
            f"Account deletion failed: {user_id} is not registered"
        )

        await message.answer(
            "You are not registered 🚫", reply_markup=ReplyKeyboardRemove()
        )


@router.message(ConfirmForm.confirm)
async def handle_invalid_option(message: Message) -> None:
    await message.answer(
        "Please, select an option from the list below.",
        reply_markup=get_yes_no_keyboard(),
    )
