from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from src.platform.telegram.util.menu.options import (
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


def get_profile_menu_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=BackOption.BACK)
    for option in ProfileMenuOption:
        builder.button(text=option)
    builder.adjust(3)

    return builder.as_markup(resize_keyboard=True)


def get_transactions_menu_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=BackOption.BACK)
    for option in TransactionsMenuOption:
        builder.button(text=option)
    builder.adjust(3)

    return builder.as_markup(resize_keyboard=True)
