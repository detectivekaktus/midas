from typing import cast
from aiogram.types import Message

from src.platform.telegram.util.currency import get_currency_list
from src.util.enums import Currency


def validate_currency(text: str) -> Currency:
    """
    Check if text is an element inside currency list from
    `src.platform.telegram.util.currency` module.

    :return: currency enum element.
    :rtype: Currency

    :raise ValueError: if text is not an element of the list.
    """
    currencies = get_currency_list()
    if text not in currencies:
        raise ValueError(f"{text} is not a valid currency")

    val = currencies.index(text) + 1
    return cast(Currency, val)


def valid_currency_filter(message: Message) -> dict[str, Currency] | None:
    """
    Aiogram filter for currencies.
    """
    try:
        text = message.text
        if not text:
            return None

        currency = validate_currency(text)
    except ValueError:
        return None

    return {"currency": currency}
