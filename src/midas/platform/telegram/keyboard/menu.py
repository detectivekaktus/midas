from enum import StrEnum
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from midas.platform.telegram.util.menu.options import (
    BackOption,
    MainMenuOption,
    ProfileMenuOption,
    TransactionsMenuOption,
)


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for option in MainMenuOption:
        builder.button(text=option)
    builder.adjust(3)

    return builder.as_markup(resize_keyboard=True)


def _get_menu_with_back_button(
    options: type[StrEnum], adjust: int = 3
) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=BackOption.BACK)
    for option in options:
        builder.button(text=option)
    builder.adjust(adjust)

    return builder.as_markup(resize_keyboard=True)


def get_profile_menu_keyboard() -> ReplyKeyboardMarkup:
    return _get_menu_with_back_button(ProfileMenuOption)


def get_transactions_menu_keyboard() -> ReplyKeyboardMarkup:
    return _get_menu_with_back_button(TransactionsMenuOption)
