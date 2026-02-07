from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from midas.platform.telegram.util.event import get_event_frequencies_list
from midas.platform.telegram.validator import SkipAnswer


def get_event_frequency_keyboard(skippable: bool = False) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for frequency in get_event_frequencies_list():
        builder.button(text=frequency)

    if skippable:
        builder.button(text=SkipAnswer.SKIP)

    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)
