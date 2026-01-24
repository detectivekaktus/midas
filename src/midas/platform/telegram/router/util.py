from typing import Any, Optional
from aiogram.types import Message, ReplyKeyboardMarkup

from midas.platform.telegram.state import FormMode
from midas.platform.telegram.validator import SkipAnswer


async def skipped_unskippable(
    message: Message,
    mode: FormMode,
    injected: Optional[Any] = object(),
    reply_markup: Optional[ReplyKeyboardMarkup] = None,
) -> bool:
    """
    Check if user input in `create` mode is skipped or invalid
    by specifying `injected` argument.

    If this condition is met, an error message is sent to the user.

    :param message: telegram message
    :type message: Message
    :param mode: current form mode
    :type mode: FormMode
    :param injected: injected field by the filter
    :type injected: Optional[Any]
    :param reply_markup: telegram keyboard with valid options
    :type reply_markup: Optional[ReplyKeyboardMarkup]
    :return: `True` if input is valid, `False` otherwise
    :rtype: bool
    """
    if mode == FormMode.CREATE and (
        injected is None or message.text == SkipAnswer.SKIP
    ):
        await message.answer("You can't skip this option.", reply_markup=reply_markup)
        return True

    return False
