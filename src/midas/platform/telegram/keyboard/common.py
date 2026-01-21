from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from src.platform.telegram.validator import SkipAnswer
from src.platform.telegram.validator import YesNoAnswer


def get_yes_no_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=YesNoAnswer.YES)
    builder.button(text=YesNoAnswer.NO)
    builder.adjust(2)

    return builder.as_markup(resize_keyboard=True)


def get_skip_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=SkipAnswer.SKIP)
    builder.adjust(1)

    return builder.as_markup(resize_keyboard=True)
