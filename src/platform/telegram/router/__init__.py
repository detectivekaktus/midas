from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.loggers import aiogram_logger
from src.service.user_caching import CachedUser

from src.platform.telegram.util.menu.events import send_main_menu

router = Router(name=__name__)


@router.message(Command("cancel"))
@router.message(F.text.casefold() == "cancel")
async def handle_global_cancel(
    message: Message, state: FSMContext, user: CachedUser
) -> None:
    """
    Allow user to cancel any state action.
    """
    current_state = await state.get_state()
    if current_state is not None:
        aiogram_logger.info(f"Canceled current action {user.id}.")
        await state.clear()

    await send_main_menu(message, state)
